import os

# Get the current directory
current_dir = os.getcwd()

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Path to the src folder
src_folder = os.path.join(parent_dir, 'TV-Alpaca-Bot', 'src')

# Change the current working directory to the src folder
os.chdir(src_folder)

os.system('export FLASK_ENV=development')

# Now you can run the "flask run" command
os.system('flask run --debug')