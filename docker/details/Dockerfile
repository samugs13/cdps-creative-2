FROM ruby:2.7.1-slim
ARG service_version
ARG enable_external_book_service
ENV SERVICE_VERSION ${service_version:-v1}
ENV ENABLE_EXTERNAL_BOOK_SERVICE ${enable_external_book_service:-true}
EXPOSE 9080
RUN apt update
RUN apt install git -y
RUN git clone https://github.com/CDPS-ETSIT/practica_creativa2.git
WORKDIR practica_creativa2/bookinfo/src/details
RUN mkdir /opt/microservices
RUN cp details.rb /opt/microservices/ 
WORKDIR /opt/microservices/
CMD [ "ruby", "./details.rb", "9080" ]
