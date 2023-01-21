# Stock-Prediction
Analysis and Prediction of stocks using Machine Learning

## Initial Setup
### Install dependencies
```bash
$ cd <dir>
$ gh repo clone sarthak7gupta/Stock-Prediction
$ cd Stock-Prediction

$ curl https://pyenv.run | bash
$ sudo apt install -y libbz2-dev liblzma-dev

$ pyenv install 3.8.6
$ pyenv virtalenv 3.8.6 capstone
$ pyenv local capstone

$ pip install -U pip
$ pip install -r requirements.txt
```

### Setup databases, folders and directories
```bash
$ export <MYSQL|POSTGRES>_PASSWORD=<password>

$ ./db_term.sh [MYSQL|POSTGRES]
$ ./db_init.sh [MYSQL|POSTGRES]
```
<!--
## Fetching data
<table>
<tr>
<th> StockPrice data </th>
<th> Articles data [INACTIVE] DO NOT USE</th>
</tr>
<tr>
<td>

`$ python data_service.py`

#### Import from dump
`$ gunzip -c database/dump.sql.gz | mysql -h 127.0.0.1 -P 3306 -u root -D capstone -p`
#### Export to dump
`$ mysqldump -h 127.0.0.1 -P 3306 -u root -p capstone | gzip > database/dump.sql.gz`

</td>
<td>

`$ python article_service.py`
#### Import from dump
`$ mongorestore --db=capstone --archive=database/dump.nosql.gz --gzip`
#### Export to dump
`$ mongodump --forceTableScan --db=capstone --archive=database/dump.nosql.gz --gzip`
</td>
</tr>
</table> -->

## Getting data and training models
#### To manually get stock data and train models (recommended for testing),
```
$ python data_service.py  # First run takes upto 20 minutes
$ python train_models.py  # First run takes upto 10 minutes
```

#### or to setup daemon to get data and train models daily automatically (not recommended for testing),
```
$ python cron.py &
```
##### or setup a service to run cron.py

## For Web UI,
```
$ python app.py
```
### then go to http://localhost:5000/ on your browser

## For CLI,
```
$ python ui_predictions.py
$ python ui_backtesting.py
```
