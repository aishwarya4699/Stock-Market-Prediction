import logging
from datetime import datetime
from time import mktime, sleep

import feedparser
import newspaper
from bs4 import BeautifulSoup
from tqdm import tqdm

from config import Config
from database.NoSQLModel import Article, Entry, Feed
from db_helper import connect_mongo
from sentiment import classify

logger = logging.getLogger("fetch")

urls = Config.RSSURLS

connect_mongo()


def run_service():
    n = len(urls)
    logger.info(f"Fetching from {n} RSS Feeds\n")
    for i, (key, url) in enumerate(urls.items(), 1):
        logger.info(f"{i}/{n} Fetching {key} feed...")

        try:
            f = feedparser.parse(url)
            feed_metadata = f.feed
            feed = Feed.objects(href=url).first()

            title = feed_metadata.title
            if feed_metadata.title_detail.type == "text/html":
                title = " ".join(BeautifulSoup(title).stripped_strings)

            subtitle = feed_metadata.subtitle
            if feed_metadata.subtitle_detail.type == "text/html":
                subtitle = " ".join(BeautifulSoup(subtitle, features="lxml").stripped_strings)

            generator = feed_metadata.generator

            updated_struct_time = f.updated_parsed
            last_updated = (
                datetime.fromtimestamp(mktime(updated_struct_time)) if updated_struct_time else None
            )

            if feed:
                if feed.last_updated < last_updated:
                    feed.update(set__title=title)
                    feed.update(set__subtitle=subtitle)
                    feed.update(set__generator=generator)
                    feed.update(set__last_updated=last_updated)

                else:
                    continue

            else:
                feed = Feed(
                    href=url,
                    title=title,
                    subtitle=subtitle,
                    generator=generator,
                    last_updated=last_updated,
                )

            feed_ref = feed.to_dbref()

        except Exception as e:
            logger.error(f"Error while getting {key} feed.{e}")
            continue

        for e in tqdm(f.entries, desc=f"Fetching articles from {key} feed.", unit="article"):
            try:
                link = e.link

                if entry := Entry.objects(link=link).first():
                    continue

                title = e.title
                if e.title_detail.type == "text/html":
                    title = " ".join(BeautifulSoup(title).stripped_strings)

                summary = e.summary
                if e.summary_detail.type == "text/html":
                    summary = " ".join(BeautifulSoup(summary, features="lxml").stripped_strings)

                published_struct_time = e.published_parsed
                published = (
                    datetime.fromtimestamp(mktime(published_struct_time))
                    if published_struct_time
                    else None
                )

                a = newspaper.Article(link)
                a.download()
                a.parse()
                a.nlp()

                sentiment = classify(a.text)

                if a.summary == "you are here:":
                    continue

                article = Article(
                    title=a.title,
                    html=a.html,
                    tags=a.tags,
                    keywords=a.keywords,
                    summary=a.summary,
                    text=a.text,
                )

                entry = Entry(
                    link=link,
                    title=title,
                    summary=summary,
                    published=published,
                    feed=feed_ref,
                    article=article,
                    sentiment=sentiment,
                )

                feed.entries.append(entry.to_dbref())
                entry.save()
                feed.save()

            except Exception as e:
                logger.error(f"Error while getting an article from {key} feed. {e}")

            finally:
                sleep(10)


if __name__ == "__main__":
    run_service()
