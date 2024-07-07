## インストール
```
git clone https://github.com/nOjms-Blue/PyJSON.git
cd PyJSON
pip install .
```

## 使い方
```
import pyjson

print(pyjson.read("[ 0, 1, 2, 3 ]"))
print(pyjson.read("{ id: 1, value: 'Hello, World.' }"))
```
出力
```
[0, 1, 2, 3]
{'id': 1, 'value': 'Hello, World.'}
```