FROM ubuntu:22.04

WORKDIR /cdmo
COPY . .


# Install dependencies
RUN apt update && apt install -y python3 python3-pip wget unzip
RUN pip3 install -r requirements.txt

# Install MiniZinc
RUN apt install -y libglu1-mesa-dev libegl1
RUN wget https://github.com/MiniZinc/MiniZincIDE/releases/download/2.8.4/MiniZincIDE-2.8.4-bundle-linux-x86_64.tgz &&\
    tar -xf MiniZincIDE-2.8.4-bundle-linux-x86_64.tgz &&\
    mv MiniZincIDE-2.8.4-bundle-linux-x86_64 minizinc &&\
    cp -r minizinc/bin/* /usr/local/bin &&\
    cp -r minizinc/lib/* /usr/local/lib &&\
    cp -r minizinc/share/* /usr/local/share &&\
    cp -r minizinc/lib/* /usr/local/lib

# Install CVC5
RUN wget https://github.com/cvc5/cvc5/releases/download/cvc5-1.2.0/cvc5-Linux-x86_64-static.zip &&\
    unzip cvc5-Linux-x86_64-static.zip -d cvc5 &&\
    cp -r cvc5/cvc5-Linux-x86_64-static/bin/* /usr/local/bin &&\
    cp -r cvc5/cvc5-Linux-x86_64-static/include/* /usr/local/include &&\
    cp -r cvc5/cvc5-Linux-x86_64-static/lib/* /usr/local/lib

# Install OpenSMT
RUN wget https://github.com/usi-verification-and-security/opensmt/releases/download/v2.7.0/opensmt-2.7.0-x64-linux.tar.bz2 &&\
    tar -xf opensmt-2.7.0-x64-linux.tar.bz2 &&\
    cp opensmt /usr/local/bin/opensmt


RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]