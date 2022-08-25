from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
from functools import partial
from myfirebase import MyFirebase
from bannervendedor import BannerVendedor
from datetime import date


GUI = Builder.load_file('main.kv')
class MainApp(App):
    cliente = None
    produto = None
    unidade = None


    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):
        '''
        Função responsável para carregar os arquivos iniciais, ex: As fotos de Perfil, dos clientes e
        dos produtos, a data atual e informações do usuário.
        :param: Nenhum
        :return: Retorna os arquivos necessários do sistema e do usuário.
        '''
        # Carregar as fotos do perfil
        arquivos = os.listdir('icones/fotos_perfil')
        pagina_fotos_perfil = self.root.ids['fotoperfilpage']
        lista_fotos_perfil = pagina_fotos_perfil.ids['lista_fotos_perfil']
        for foto in arquivos:
            imagem = ImageButton(source=f'icones/fotos_perfil/{foto}', on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos_perfil.add_widget(imagem)

        # Carregar as fotos dos Clientes
        arquivos = os.listdir('icones/fotos_clientes')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        listas_clientes = pagina_adicionarvendas.ids['lista_clientes']
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f'icones/fotos_clientes/{foto_cliente}',
                                 on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace('.png', '').capitalize(),
                                on_release=partial(self.selecionar_cliente, foto_cliente))
            listas_clientes.add_widget(imagem)
            listas_clientes.add_widget(label)

        # Carregar as fotos dos Produtos
        arquivos = os.listdir('icones/fotos_produtos')
        lista_produtos = pagina_adicionarvendas.ids['lista_produtos']
        for foto_produto in arquivos:
            imagem = ImageButton(source=f'icones/fotos_produtos/{foto_produto}',
                                 on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace('.png', '').capitalize(),
                                on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        # Carregar a Data atual
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        label_data = pagina_adicionarvendas.ids['label_data']
        label_data.text = f'Data: {date.today().strftime("%d/%m/%Y")}'

        # Carregar as infos do usuário
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        '''
        Função responsável por carregar as informações do usuário, como id_vendedor, foto perfil, total
        de vendas, lista de vendas e a equipe de vendedores.
        :param: Nenhum
        :return: Retorna os arquivos necessários do usuário.
        '''
        try:
            with open('refreshtoken.txt', 'r') as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # Pegando informações do Banco de Dados
            requisicao = requests.get(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requisicao_dic = requisicao.json()

            # Preencher a foto de perfil do usuário
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']

            # Preencher o Id_vendedor
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f'Seu ID Único: {id_vendedor}'

            # Preencher o total_vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            pagina_homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

            # Preencher lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                         produto=venda['produto'], foto_produto=venda['foto_produto'],
                                         data=venda['data'], preco=venda['preco'],
                                         unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except Exception as excessao:
                print(excessao)
                pass

            # Preencher equipe de vendedores
            equipe = requisicao_dic["equipe"]
            self.equipe = equipe
            lista_equipe = equipe.split(",")
            pagina_listavendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != '':
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela('homepage')

        except:
            pass

    def mudar_tela(self, id_tela):
        '''
        Função responsável para mudar de tela.
        :param id_tela: Id da tela do botão selecionado.
        :return: Retorna para uma tela específica.
        '''
        gerenciador_tela = self.root.ids['screen_manager']
        gerenciador_tela.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        '''
        Função responsável para mudar a foto de perfil do usuário.
        :param foto: Foto selecionada pelo usuário.
        :param args:
        :return: Retorna nova foto de perfil do usuário.
        '''
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'

        info = f'{{"avatar": "{foto}"}}'  # passando a info no formato str.
        requisicao = requests.patch(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                    data=info) # data requer dados no formato str.
        self.avatar = foto
        self.mudar_tela('ajustespage')

    def adicionar_vendedor(self, id_adicionado):
        '''
        Função responsável para adicionar vendedor na lista da equipe.
        :param id_adicionado: id do vendedor que deseja adicionar.
        :return: Retorna Banner de vendedor (Equipe)
        '''
        link = f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        pagina_adicionarvendedor = self.root.ids['adicionarvendedorespage']
        mensagem = pagina_adicionarvendedor.ids['mensagem_adicionarvendedor']

        # Verificando se o id digitado existe no banco de dados.
        if requisicao_dic == {}:
            mensagem.text = 'Usuário não encontrado'
        else:
            equipe = self.equipe.split(',')
            # Verificando se o id digitado já faz parte da equipe.
            if id_adicionado in equipe:
                mensagem.text = 'Usuário já faz parte da equipe'
            else:
                # Caso id ainda não faz parte da equipe, adiciona o vendedor na lista da equipe.
                self.equipe = self.equipe + f',{id_adicionado}'
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                            data=info)
                mensagem.text = 'Usuário adicionado com sucesso'

                # Adicionar um novo banner na lista de vendedores
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):
        '''
        Função responsável para selecionar o cliente e mudar a cor das letras quando selecionado.
        :param foto: foto do cliente
        :param args:
        :return: Retorna o cliente selecionado com a cor Azul
        '''
        self.cliente = foto.replace('.png', '')
        # Pintar de Branco todas as letras
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        listas_clientes = pagina_adicionarvendas.ids['lista_clientes']
        for item in list(listas_clientes.children):
            item.color = (1, 1, 1, 1)

            # Pintar de Azul a letra do cliente que selecionamos
            # foto = carrefour.png / Label = Carrefour / transformar em minuscula e adicionar .png
            # Vamos tentar pintar o label do cliente, caso seja a imagem não podemos pintar
            try:
                texto = item.text
                texto = texto.lower() + '.png'
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        '''
        Função responsável por selecionar o produto e mudar a cor das letras quando selecionado.
        :param foto: Foto do Produto
        :param args:
        :return: Retorna o produto selecionado com a cor Azul
        '''
        self.produto = foto.replace('.png', '')
        # Pintar de Branco todas as letras
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        listas_produtos = pagina_adicionarvendas.ids['lista_produtos']
        for item in list(listas_produtos.children):
            item.color = (1, 1, 1, 1)

            # Pintar de Azul a letra do produto que selecionamos
            # foto = arroz.png / Label = arroz / transformar em minuscula e adicionar .png
            # Vamos tentar pintar o label do produto, caso seja a imagem não podemos pintar
            try:
                texto = item.text
                texto = texto.lower() + '.png'
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        '''
        Função responsável por selecionar a unidade e mudar a cor quando selecionado.
        :param id_label: Id correspondente a label da unidade
        :param args:
        :return: Retorna a unidade selecionada com a cor Azul
        '''
        self.unidade = id_label.replace('unidades_', '')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        # Pintar todas as unidades de Branco
        pagina_adicionarvendas.ids['unidades_kg'].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids['unidades_unidades'].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids['unidades_litros'].color = (1, 1, 1, 1)

        # Pintar a unidade selecionada de Azul
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        '''
        Função responsável por adicionar venda
        :return: Retorna um Banner de venda com a venda adicionada.
        '''
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        data = date.today().strftime('%d/%m/%Y') # Data atual que estará no label da data
        preco = pagina_adicionarvendas.ids['input_preco_total'].text
        quantidade = pagina_adicionarvendas.ids['input_quantidade_total'].text

        # Verificando se os campos estão todos preenchidos
        if not cliente:
            pagina_adicionarvendas.ids['label_selecione_cliente'].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids['label_selecione_produto'].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids['unidades_kg'].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids['unidades_unidades'].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids['unidades_litros'].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids['label_preco_total'].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids['label_preco_total'].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionarvendas.ids['label_quantidade_total'].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids['label_quantidade_total'].color = (1, 0, 0, 1)

        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_cliente = cliente + '.png'
            foto_produto = produto + '.png'

            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", ' \
                   f'"data": "{data}", "preco": "{preco}", "unidade": "{unidade}", "quantidade": "{quantidade}"}}'
            requests.post(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}', data=info)

            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            banner = BannerVenda(cliente=cliente, foto_cliente=foto_cliente, produto=produto, foto_produto=foto_produto,
                                 data=data, unidade=unidade, preco=preco, quantidade=quantidade)
            lista_vendas.add_widget(banner)

            requisicao = requests.get(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}')
            total_vendas = float(requisicao.json())
            total_vendas += preco
            info_total = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f'https://aplicativovendas-47f91-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                              data=info_total)

            pagina_homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'
            self.mudar_tela('homepage')

        # Depois de adicionar os valores da venda, Zerar as variareis Cliente, Produto, Unidade
        self.cliente = None
        self.produto = None
        self.unidade = None

    def todas_vendas_empresa(self):
        '''
        Função responsável por carregar um banner com todas as vendas da empresa, com as informações de
        cada vendedor e a venda de cada um.
        :return: Retorna um Banner de todas as vendas da empresa.
        '''
        # Antes de adicionar os banners das vendas, vamos deletar todos os que ja existe.
        pagina_todasvendas = self.root.ids['todasvendaspage']
        lista_vendas = pagina_todasvendas.ids['lista_vendas']

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # Preencher a pagina de todas as vendas
        # Pegando informações do Banco de Dados
        requisicao = requests.get('https://aplicativovendas-47f91-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()

        # Preencher a foto de perfil da empresa
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = 'icones/fotos_perfil/hash.png'

        # Preencher o total de Vendas da empresa
        total_vendas = 0

        # Preencher o Scrollview com os banner das vendas da empresa
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                                  produto=venda['produto'], foto_produto=venda['foto_produto'],
                                                  data=venda['data'], preco=venda['preco'],
                                                  unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except:
                pass

        # Preencher o total_vendas
        pagina_todasvendas.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

        # Mudar a tela para a pagina de todas as vendas da empresa
        self.mudar_tela('todasvendaspage')

    def sair_todas_vendas(self, id_tela):
        '''
        Função responsável por volta da tela de todas as vendas da empresa e trocar a foto de perfil da
        empresa para a foto do usuário.
        :param id_tela: id da tela ajustespage.
        :return: Retorna para a tela de ajustespage.
        '''
        # Mudar para a foto do usuário
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'
        # Voltar para a página desejada
        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):
        '''
        Função responsável por carregar todas as vendas do vendedor específico, e criar um Banner de venda
        para cada venda.
        :param dic_info_vendedor: Dicionário de informações do vendedor selecionado.
        :param args:
        :return: Retorna um Banner de Vendas de um vendedor específico.
        '''
        pagina_outrovendedor = self.root.ids['vendasoutrovendedorpage']
        lista_vendas = pagina_outrovendedor.ids['lista_vendas']
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)
        try:
            vendas = dic_info_vendedor['vendas']
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                     produto=venda['produto'], foto_produto=venda['foto_produto'],
                                     data=venda['data'], preco=venda['preco'],
                                     unidade=venda['unidade'], quantidade=venda['quantidade'])
                lista_vendas.add_widget(banner)
        except Exception as excessao:
            print(excessao)
            pass
        # Preencher o total de vendas
        total_vendas = dic_info_vendedor['total_vendas']
        pagina_outrovendedor.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R${total_vendas}[/b]'

        # Preencher a foto de perfil
        foto_perfil = self.root.ids['foto_perfil']
        avatar = dic_info_vendedor['avatar']
        foto_perfil.source = f'icones/fotos_perfil/{avatar}'

        # Mudar a tela
        self.mudar_tela('vendasoutrovendedorpage')

MainApp().run()