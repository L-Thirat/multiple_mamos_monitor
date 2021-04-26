v1.0

Python
https://www.python.org/downloads/release/python-353/

install
pip install -r requirements.txt

Docker 
https://docs.docker.com/docker-for-windows/install-windows-home/
docker run -d -it -p 5000:5000 --name=few2012few/mamos-hub:lastest
docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
docker run -d --name watchtower -v /var/run/docker.sock:/var/run/docker.sock v2tec/watchtower few2012few/mamos-hub:lastest