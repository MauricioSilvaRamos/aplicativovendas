import requests
from kivy.app import App


class MyFirebase():
    '''
    Classe respondável pelo Banco de Dados.
    '''
    API_KEY = 'AIzaSyB63pvD8MBkmjVJnlMm7yDZugUR9m9XqfI'

    def criar_conta(self, email, senha):
        '''
        Função responsável para criar conta do usuário.
        :param email: E-mail do usuário
        :param senha: Senha do usuário
        :return: Retorna o cadrastro do usuário no app.
        '''
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'
        info = {'email': email, 'password': senha, 'returnSecureToken': True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            # requisicao['idToken'] -> Autenticação
            # requisicao['localId'] -> Id do usuario no banco de dados
            # requisicao['refreshToken'] -> Token que Mantém o usuário logado
            id_token = requisicao_dic['idToken']
            local_id = requisicao_dic['localId']
            refresh_token = requisicao_dic['refreshToken']
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.id_token = id_token
            meu_aplicativo.local_id = local_id

            with open('refreshtoken.txt', 'w') as arquivo:
                arquivo.write(refresh_token)

            rec_id_vendedor = requests.get(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}')
            id_vendedor = rec_id_vendedor.json()

            link = f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}'
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)

            # Atualizar o proximo_id_vendedor
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/.json?auth={id_token}', data=info_id_vendedor)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('homepage')

        else:
            messagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['loginpage']
            pagina_login.ids['mensagem_login'].text = messagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):
        '''
        Função responsável por fazer login do usuário que já tenha cadrastrado no banco de dados do app e
        por verificar se o usuário já tenha feito login antes, então loga direto no app.
        :param email: E-mail do usuário
        :param senha: Senha do usuário
        :return: Loga o usuário no app.
        '''
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
        info = {'email': email, 'password': senha, 'returnSecureToken': True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            id_token = requisicao_dic['idToken']
            local_id = requisicao_dic['localId']
            refresh_token = requisicao_dic['refreshToken']
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.id_token = id_token
            meu_aplicativo.local_id = local_id

            with open('refreshtoken.txt', 'w') as arquivo:
                arquivo.write(refresh_token)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('homepage')

        else:
            messagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['loginpage']
            pagina_login.ids['mensagem_login'].text = messagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):
        '''
        Função responsável por trocar o token do usuário.
        :param refresh_token:  refresh_token do usuário.
        :return: Retorna o local_id e id_token do usuário.
        '''
        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'

        info = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']
        return local_id, id_token
