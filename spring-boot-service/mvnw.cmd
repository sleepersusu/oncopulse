@REM ----------------------------------------------------------------------------
@REM Maven Wrapper startup batch script
@REM ----------------------------------------------------------------------------
@IF "%__MVNW_ARG0_NAME__%"=="" (SET __MVNW_ARG0_NAME__=%~nx0)
@SET @@MVNW_LAUNCHER=%~dp0.mvn\wrapper\maven-wrapper.jar
@SET @@MAVEN_JAVA_EXE=%JAVA_HOME%\bin\java.exe
@IF NOT EXIST %@@MAVEN_JAVA_EXE% SET @@MAVEN_JAVA_EXE=java.exe
@SET MAVEN_PROJECTBASEDIR=%~dp0
"%@@MAVEN_JAVA_EXE%" -classpath "%@@MVNW_LAUNCHER%" ^
  "-Dmaven.multiModuleProjectDirectory=%MAVEN_PROJECTBASEDIR%" ^
  org.apache.maven.wrapper.MavenWrapperMain %*
