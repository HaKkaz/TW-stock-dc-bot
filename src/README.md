# Testing 


### Fuzz test

run the fuzz-test

```
chmod 777 ./src/fuzz-test.py
py-afl-fuzz -i ./src/input -o ./src/output -- ./src/fuzz-test.py
```
