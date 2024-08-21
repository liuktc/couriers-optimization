FROM ubuntu:22.04

WORKDIR /cdmo
COPY . .


# Install dependencies
RUN apt update && apt install -y python3 python3-pip wget
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

# Install amplpy and all necessary amplpy.modules:
RUN python -m pip install amplpy --no-cache-dir # Install amplpy
RUN python -m amplpy.modules install highs gurobi --no-cache-dir # Install modules

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]