from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#1° Criar uma api flask
app = Flask(__name__)


#Usar esse comando abaixo "app.app_context():" antes de mais nada e dentro dele(indentado) jogamos a lógica do banco.
with app.app_context():

    #2° Criar uma instância de SQLAlchemy
    app.config['SECRET_KEY'] = 'asdbc36555@#$%???oeyrnsmnakaaa'#Autenticação
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:7r9CrfkR6jxWkoIyX4ZR@containers-us-west-88.railway.app:7830/railway'#string de conexão do banco de dados

    db = SQLAlchemy(app)
    db: SQLAlchemy#tipando a variável ou seja deixando statica.


    #Definir a estrutura da tabela Postagem
    #id_postagem, titulo, autor
    class Postagem(db.Model):
        __tablename__ = 'postagem'#Definindo o nome da tabela
        id_postagem = db.Column(db.Integer, primary_key=True)#Chave primária da tabela postagem
        titulo = db.Column(db.String)
                                                    #tabela.chave_primaria
        id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))#Chave estrangeira da tabela autor


    #Definir a estrutura da tabela Autor
    #id_autor, nome, email, senha, admin, postagens     
    class Autor(db.Model):
        __tablename__ = 'autor'
        id_autor = db.Column(db.Integer, primary_key=True)#Chave primária da tabela autor
        nome = db.Column(db.String)
        email = db.Column(db.String)
        senha = db.Column(db.String)
        admin = db.Column(db.Boolean)
        postagens = db.relationship('Postagem')#Aqui estamos realizando o relacionamento com a tabela postagem porém temos que passar a classe como parâmetro.
    
    
    #Função para evitar que drop o banco toda vez que rodar o arquivo
    def inicializar_banco():
        with app.app_context():
            #Executar o comando para criar o banco de dados
            db.drop_all()
            db.create_all()
            
            #Criar usuários administradores
            autor = Autor(nome='Anderson', email='anderson@teste.com', senha='123456', admin=True)
            db.session.add(autor)
            db.session.commit()
    
    #Condicional para verificar se o arquivo é o main e se for vai rodar a função de inicializar banco.
    if __name__ == '__main__':
        inicializar_banco()
    
    
    
    
