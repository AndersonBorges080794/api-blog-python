from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db#Importando classes, funções e variáveis do arquivo "estrutura_banco_de_dados"
import json
import jwt
from datetime import datetime, timedelta
from functools import wraps

#API(postagem) com conexão ao banco de dados(banco SQLite)

#Função que vai exigir autenticação na rota que ela estiver.
#Aqui está toda lógica de como deixar uma rota autenticada.
def token_obrigatorio(f):
    @wraps(f)#wraps da biblioteca wraps.
    def decorated(*args, **kwargs):
        token = None#Setando None no token como valor incial
        
        #Validação para verificar se o parâmetro 'x-access-token' está sendo passada no headers da requisição e se for verdadeiro
        #irá passar o token da requisição para variável token.
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']#Token que é passado na requisição será atribuido na variável token.   
        
        #Validação para verificar se o token de fato possui valor e caso ele não tenha irá retornar uma mensagem dizendo que o token não foi incluído.
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        
        #Lógica para realizar a decodificação do token.
        try:
            #Aqui estamos decodificando o token que foi recebido da requisição.
            #1 - (token, token da requisição;
            #2 - app.config['SECRET_KEY'], string com caracteres que está no arquivo "estrutura_banco_de_dados.py";
            #3 - algorithms=["HS256"]) tipo do algoritmo usado na decodificação. 
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            #Aqui vamos buscar por 'id_autor' no DB a informação que é passada na requisição.
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        
        #Bloco para retornar uma mensagem de erro caso o bloco try dê algum erro.
        except:
            return jsonify({'mensagem': 'Token é inválido'}, 401)
        
        #retornamos a função 'f' com o parâmetro autor, todos os argumentos posicionais e todos os argumentos nomeados.
        return f(autor, *args, **kwargs)
    
    return decorated  
               

#Rota que gera o token JWT que vai ser utilizado nas outras rotas que necessita de autenticação.
#Aqui está toda lógica de como gerar um token JWT.
@app.route('/login')
def login():
    auth = request.authorization#Aqui estamos pegando as informações de usuário e senha da requisição.
    
    #Condicional para verificar se na requisição está vazio por completo, ou username está vazio, ou password está vazio
    #se algum cenário desse for verdadeiro vai retornar codigo 401
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    
    #Buscando no DB se esse usuário que veio da requisição existe.
    usuario = Autor.query.filter_by(nome=auth.username).first()
    
    #Condicional para verificar caso o usuario que foi passado na requisição não exista dentro do DB vai retornar o mesmo erro codigo 401.
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    
    #Condicional para verificar se a senha passada na requisição é igual a senha cadastrada no DB se for verdadeiro irá entrar no bloco.
    if auth.password == usuario.senha:
        
        #código que irá gerar o token e ele segue a seguinte lógica:
        #1 - ({'id_autor':usuario.id_autor, é usuário recuperado do DB;
        #2 - 'exp':datetime.utcnow() + timedelta(minutes=30)}, é o tempo de expiração do token que diz tempo gerada atual + tempo de 30 minutos;
        #3 - app.config['SECRET_KEY']) é a string de caracteres que fizemos no arquivo "estrutura_banco_de_dados.py";
        #4 - return jsonify({'token': token}) retorno do token gerado.
        token = jwt.encode({'id_autor':usuario.id_autor, 'exp':datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    
    #Retorno caso o usuário deigite a senha errada.
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
      

#Rota padrão - GET - http://localhost:7777
@app.route('/')
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def obter_postagens(autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    postagens = Postagem.query.all()
    lista_postagens = []
    
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_postagens.append(postagem_atual)
    return jsonify({'postagens': lista_postagens})

#Para executar aplicação flask sempre se atentar nos parâmetros port, host e debug. Tendo em vista que port pode ser qualquer um
#o host deixa como padrão o "localhost" e debug fica opção True ou False.
# app.run(port=7777, host='localhost', debug=True)


#Obter postagem por id - GET - http://localhost:7777/postagem/1
@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def obter_postagens_por_indice(autor, id_postagem):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    postagem = Postagem.query.filter_by(id_postagem = id_postagem).first()
    postagem_atual = {}
    
    if not postagem:
        return jsonify(f'Postagem não encontrada!')
    
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    
    postagem_atual['id_autor'] = postagem.id_autor
    
    return jsonify({'postagem': postagem_atual})#Retorna em forma de dicionário
     

#Criar uma nova postagem - POST - http://localhost:7777/postagem
@app.route('/postagem', methods=['POST'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def nova_postagem(autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    nova_postagem = request.get_json()
    postagem = Postagem(titulo = nova_postagem['titulo'], id_autor = nova_postagem['id_autor'])
    db.session.add(postagem)
    db.session.commit()
    
    return jsonify({'mensagem': 'Postagem criada com sucesso'}, 200)


#Alterar uma postagem existente - PUT - http://localhost:7777/postagem/0
@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def alterar_postagem(autor, id_postagem):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    postagem_a_alterar = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem = id_postagem).first()
    
    if not postagem:
        return jsonify({'mensagem': 'Esta postagem não foi encontrada'})
    
    try:
        postagem.titulo = postagem_a_alterar['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_a_alterar['id_autor']
    except:
        pass
        
    db.session.commit()
    
    return jsonify({'mensagem': 'Postagem alterada com sucesso!'})


#Exluir uma postagem existente - DELETE - http://localhost:7777/postagem/0
@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def excluir_postagem(autor, id_postagem):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    postagem_a_excluida = Postagem.query.filter_by(id_postagem = id_postagem).first()
    
    if not postagem_a_excluida:
        return jsonify({'mensagem': 'Esta postagem não foi encontrado'})
    
    db.session.delete(postagem_a_excluida)
    db.session.commit()
    
    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})
    
    
###################################################################################################################################

#API(autor) com conexão ao banco de dados(banco SQLite)

#Rota recupera todos autores banco de dados
@app.route('/autores')
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
#Função que busca todos os autores dentro do banco.
def obter_autores(autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    autores = Autor.query.all()#Recuperando os dados do banco de dados
    lista_de_autores = []
    
    for autor in autores:
       autor_atual = {}
       autor_atual['id_autor'] = autor.id_autor
       autor_atual['nome'] = autor.nome
       autor_atual['email'] = autor.email
       lista_de_autores.append(autor_atual)
    
    return jsonify({'autores': lista_de_autores})#Retorna em forma de dicionário

#Rota que recupera os dados do banco por id
@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
#Função que busca o autor por id dentro do banco
def obter_autor_por_id(autor, id_autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    autor = Autor.query.filter_by(id_autor = id_autor).first()#Recuperando os dados por id dentro do banco de dados
    
    if not autor:
        return jsonify(f'Autor não encontrado!')
    
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    
    return jsonify({'autor': autor_atual})#Retorna em forma de dicionário

#Rota que realiza o inserte dados dentro do banco
@app.route('/autores', methods=['POST'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
#Função que cria um novo autor dentro do banco
def novo_autor(autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    novo_autor = request.get_json()
    autor = Autor(nome = novo_autor['nome'], senha = novo_autor['senha'], email = novo_autor['email'])
    db.session.add(autor)
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário criado com sucesso'}, 200)

#Rota que realiza alteração de dados existentes dentro do banco
@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def alterar_autor(autor, id_autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor = id_autor).first()
    
    if not autor:
        return jsonify({'mensagem': 'Este usuário não foi encontrado'})
    
    try:
        autor.nome = usuario_a_alterar['nome']
    except:
        pass
    
    try:
        autor.email = usuario_a_alterar['email']
    except:
        pass
    
    try:
        autor.senha = usuario_a_alterar['senha']
    except:
        pass
    
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário alterado com sucesso!'})

#Rota que realiza a exclusão de dados existentes dentro do banco
@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio#A rota que tiver esse decorador quer dizer que só pode ser acessada com o token JWT de autenticação.
def excluir_autor(autor, id_autor):#O parâmetro 'autor' deve ser passada como o primeiro em todas as rotas para funcionar autenticação via toke JWT.
    autor_existente = Autor.query.filter_by(id_autor = id_autor).first()
    
    if not autor_existente:
        return jsonify({'mensagem': 'Este autor não foi encontrado'})
    
    db.session.delete(autor_existente)
    db.session.commit()
    
    return jsonify({'mensagem': 'Autor excluído com sucesso!'})


    
app.run(port=7777, host='localhost', debug=True)

