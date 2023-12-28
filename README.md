![Locker Password Manager](https://raw.githubusercontent.com/lockerpm/.github/main/images/locker2.png)

-------------------

## Locker API

Locker API is a project that serves as the backend for the Locker Password Manager, an end-to-end encryption software 
that allows users to securely store and manage their sensitive data and secrets. This repository contains the 
server-side code and functionalities that enable users to interact with the Locker through API calls.

## Developer Documentation

### Setup Guide

This section will show you how to set up a local Locker server for development purposes.

#### Clone the repository

1. Clone the Locker Server project:

```
git clone -b selfhosted https://github.com/lockerpm/api.git
```

2. Open a terminal and navigate to the root of the cloned repository


#### Config environment variables

1. Copy the example environment file

```
cp dev/.env.example .env
```

2. Open `.env` with your preferred editor.

3. Change your environment variables or use their default values. Save and quit this file.


#### Run local server

1. Use the virtual environment and active the virtual environment
```
python -m  venv <virtual-environment-name>
```

```
source venv/bin/active
```

2. Install requirements.txt

```
pip install -r requirements.txt
```

3. Run the database migrations and start local server

```
python manage.py migrate
```

```
python manage.py runserver 127.0.0.1:8000
```

Now, the local server will be run at `http://127.0.0.1:8000`


### Database

Locker Server primarily stores data in MySQL. The data access layer uses the Django ORM.

#### Update the database

You should run the `python manage.py migrate` command helper whenever you sync the new version from repository or create 
a new migration script. 

#### Modifying the database

The process for modifying the data is described in `locker_server/api_orm/migrations` folders.


### Environment variables

1. Databases

- MYSQL_USERNAME: Your Database username
- MYSQL_PASSWORD: Your Database password
- MYSQL_DATABASE: The database name
- MYSQL_HOST: The database host
- MYSQL_PORT: The MySQL port

Example
```
MYSQL_USERNAME=root
MYSQL_PASSWORD=rootmysqlpassword
MYSQL_DATABASE=locker
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

2. Caching

The Locker Server use Redis as caching database

- CACHE_LOCATION: The redis location

Example
```
CACHE_LOCATION=redis://:@127.0.0.1:6379/1
```

3. WebSocket channels

- CHANNEL_REDIS_LOCATION: The redis location to run websocket channel

Example
```
CHANNEL_REDIS_LOCATION=redis://:@127.0.0.1:6379/1?ssl_cert_reqs=none
```


## API Documentation
For detailed API documentation, refer to the [documentation website](https://docs.locker.io/).


## Whitepaper

[Locker Whitepaper](https://locker.io/whitepaper)


## Contribute

Contributions to the Locker API project are welcome! If you find any issues or want to suggest improvements, please 
feel free to open an issue or submit a pull request.

Before contributing, please review the [Contribution Guidelines](https://github.com/lockerpm/.github/blob/main/CONTRIBUTING.md).


## License

The Locker API Backend is open-source and released under the [GPLv3](./LICENSE) License. Feel free to use, modify, and 
distribute the code as per the terms of the license.