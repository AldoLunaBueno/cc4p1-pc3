FROM maven:3.9-eclipse-temurin-17

WORKDIR /app

# Copiamos la configuración de Maven y el código fuente
COPY pom.xml .
COPY src ./src

# Compilamos y ejecutamos la clase Main
CMD ["mvn", "compile", "exec:java", "-Dexec.mainClass=uni.Main"]