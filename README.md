# Money Mover

## Code Spaces initialization with a bank

To simulate a bank, create a code space, and execute the following commands:

```sh
cd bank
```

Once you are there, create a file called `.env` and inside, create the following variables:

```sh
CBU_PREFIX=1234567
SECRET=<KEY>
```

```Note: If you are going to create many banks, change the CBU_PREFIX between banks.```

Then, run the followings commands

```sh
./init.sh
./run.sh
```

Then, click the pop-up to make it public and go to the Ports tab. Copy the local address of port 8000 and open it in a new browser tab, adding `/docs` at the end of the path.


## Code Spaces initialization with money-mover

To simulate money-mover, create a code space, and execute the following commands:

```sh
cd money-mover
```

Once you are there, create a file called `.env` and inside, create the following variables:

```sh
1234567=Santander;http://localhost:8000/
7654321=Galicia;http://localhost:8000/
SECRET=<KEY>
```

```Note: The code of each bank must be the CBU_PREFIX of the bank created previously, with the correct local address of each bank, and the key must be the same one.```

Then, run the followings commands

```sh
./init.sh
./run.sh
```

Then, click the pop-up to make it public and go to the Ports tab. Copy the local address of port 8000 and open it in a new browser tab, adding `/docs` at the end of the path.
