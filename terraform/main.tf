########################################################
# terraform/main.tf
########################################################
provider "aws" {
  region     = "us-east-1"
}

#variable "key_name" {
#  description = "Nombre del Key Pair para SSH"
#  type        = string
#}

#variable "public_key_path" {
#  description = "Ruta a la llave pública SSH"
#  type        = string
#}

#resource "aws_key_pair" "deployer" {
#  key_name   = var.key_name
#  public_key = file(var.public_key_path)
#}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "graph_sg" {
  name        = "graph_sg"
  description = "Allow inbound on ports 80, 5000 and SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic on port 80"
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic on port 5000"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow SSH from any IP"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "graph_sg"
  }
}

resource "aws_instance" "graph_ec2" {
  ami                    = "ami-0e731c8a588258d0d"  # Verifica que este AMI existe en us-east-1
  instance_type          = "t2.micro"
  subnet_id              = tolist(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids = [aws_security_group.graph_sg.id]
#  key_name               = aws_key_pair.deployer.key_name

  associate_public_ip_address = true  # IP pública dinámica

  user_data = <<-EOF
    #!/bin/bash
    set -e
    exec > /var/log/user-data.log 2>&1

    echo "Iniciando configuración de la instancia EC2"

    # Actualizar paquetes
    dnf update -y
    echo "Actualización de paquetes completada"

    # Instalar dependencias
    dnf install -y python3-pip git nginx
    echo "Instalación de dependencias completada"

    # Clonar el repositorio
    cd /home/ec2-user
    git clone https://github.com/JoaquinIP/graphword-mj.git
    echo "Clonación del repositorio completada"

    # (1) Eliminar/renombrar default.conf si existe, para evitar conflictos de server_name "_"
    if [ -f /etc/nginx/conf.d/default.conf ]; then
      mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.backup
      echo "default.conf renombrado para evitar conflicto de server_name _"
    fi

    # Navegar al directorio de la APP
    cd graphword-mj/app
    echo "Navegación al directorio de la APP completada"

    # Instalar dependencias de Python
    pip3 install -r requirements.txt
    pip3 install gunicorn flask-cors
    echo "Instalación de dependencias de Python completada"

    # Configurar Nginx como proxy inverso
    cat > /etc/nginx/conf.d/graphword.conf << EOL
    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
    EOL
    echo "Configuración de Nginx completada"

    systemctl enable nginx
    systemctl restart nginx
    echo "Nginx reiniciado"

    # Navegar al directorio de la API Flask
    cd /home/ec2-user/graphword-mj/app/api
    echo "Navegación al directorio de la API Flask completada"

    # Iniciar la API con Gunicorn (modo simple)
    nohup gunicorn --bind 127.0.0.1:5000 api:app > app.log 2>&1 &
    echo "Gunicorn iniciado"
  EOF

  tags = {
    Name = "GraphWordInstance"
  }
}

###################################################
# API Gateway
###################################################
resource "aws_apigatewayv2_api" "graph_api" {
  name          = "graph-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "http_proxy" {
  api_id             = aws_apigatewayv2_api.graph_api.id
  integration_type   = "HTTP_PROXY"

  # (2) Sin barra inclinada final
  integration_uri    = "http://${aws_instance.graph_ec2.public_dns}:80"
  connection_type    = "INTERNET"
  integration_method = "ANY"

  depends_on = [aws_instance.graph_ec2]
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.graph_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.http_proxy.id}"
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.graph_api.id
  name        = "dev"
  auto_deploy = true
}

########################################
# Outputs
########################################
output "api_endpoint" {
  value = aws_apigatewayv2_stage.dev.invoke_url
}

output "ec2_public_dns" {
  value = aws_instance.graph_ec2.public_dns
}
