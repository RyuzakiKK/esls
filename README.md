# esls
This is a university project for the "Smart Cities" and "Engineering of complex adaptive software systems" courses.
It aims to improve street lighting efficiency, allowing automation, remote management and statistics collection.
All communications are implemented through REST interfaces.

The system includes:
- many Rasperry Pi systems located on the territory, controlling nearby street lamps;
- a time series database which collects data;
- one or more servlet applications, which are bridges between the Raspberries and the database;
- a management web UI which allows to control the Raspberries remotely;
- a Grafana setup to analyze the collected data; 
- a relational database (optional) which stores support data.

esls stands for: **E**sls **S**mart **L**ight **S**ystem and also for **E**ugenio **S**everi & **L**udovico de Nitti**S**
