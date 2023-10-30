mvn clean package -B -V -e -Pspark3  -Pscala-2.12  -Pthriftserver -DskipTests  -DskipITs -Dmaven.javadoc.skip=true
