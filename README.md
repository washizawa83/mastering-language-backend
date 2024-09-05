Docker image作成
```shell
docker-compose build
```

パッケージインストール
```shell
docker-compose build --no-cache
```

パッケージ追加
```shell
docker-compose exec app poetry add パッケージ名
```

API起動
```shell
docker-compose up
```

DB接続
```shell
docker-compose exec db mysql app
```

マイグレーション
```shell
docker-compose exec app poetry run python -m api.migrate
```


