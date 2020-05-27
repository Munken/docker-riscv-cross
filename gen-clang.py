from string import Template
import os

temp = Template("""
FROM silkeh/clang:{tag}

RUN apt-get update -y \
    && apt-get install -y \
    build-essential \
    bison \
    flex 
""")

vers = [
    "9",
    "10"
]

def output_docker_file(tag):
    d = "clang-{}".format(tag)
    os.makedirs(d, exist_ok=True)
    with open("{}/Dockerfile".format(d), "w") as f:
        s = temp.substitute(tag=tag)
        f.write(s)

for v in vers:
    output_docker_file(v)

