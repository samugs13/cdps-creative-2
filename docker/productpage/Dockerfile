FROM python:3.7.7-slim
ENV GROUP_NUMBER=43
EXPOSE 80
RUN apt update
RUN apt install git -y
RUN git clone https://github.com/CDPS-ETSIT/practica_creativa2.git
WORKDIR practica_creativa2/bookinfo/src/productpage
RUN pip3 install -r requirements.txt
RUN sed -i "/block\ title/ s/}.*{/}$GROUP_NUMBER{/" templates/productpage.html
CMD [ "python", "./productpage.py", "80" ]
