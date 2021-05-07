pip install -r requirements.txt
sudo apt install postgresql-plpython3
sudo -u postgres psql < create_db.sql
./manage.py migrate
