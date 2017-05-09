# Examples

Here you will find a few examples to see peach in action as well as a virtual machine configured with Vagrant in order 
to be able to run the tests and explore the framework without polluting your env.

The first thing you will need to do to run the tests is copying the Vagrantfile placed insinde vm folder and copy it to the root
folder of peach. Once there, you can start up the vm by following this simple steps:

```shell
cd peach  # to peach's root folder
cp examples/vm/Vagrantfile .

vagrant up --provider=virtualbox

# from the same terminal or another one
vagrant ssh
```

The last command should take you to the virtual machine root. From there you can start running the tests ...


## People example
This is a simple example that shows how to create a simple api from scratch. For simplicity all the needed modules
were placed in a single file. You can find the example app for flask and falcon web frameworks.

After connecting to the vm, lets set up the env variables for python

```shell
export PYTHONPATH=/vagrant/:/vagrant/examples
```

Before launching the api, it would be nice to have some data on the database. Run a simple script that loads some data

```
cd examples/people_api/flask
python3 load_people.py
```

Now you are ready to launch the api

```shell
python3 app.py
```

Now just point your browser to the api and start making requests to the following url:
```localhost:3000/api/people```




