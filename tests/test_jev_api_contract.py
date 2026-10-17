import os,json,unittest,urllib.error
from unittest.mock import patch,MagicMock
from src.router.jev_client import JevClient

class TestJevAPIContract(unittest.TestCase):
    def response(self,confidence=0.99,domain='ORBE_FECHAMENTO_PRINCIPAL',noul=0.1):
        return {'model':'jev-1.13.0','answers':{'pipeline_domain':{'type':'choice','choice':domain,'confidence':confidence,'probabilities':{domain:1.0}},'is_delayed_batch':{'type':'noul','noul':noul}}}
    def call(self,data):
        response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps(data).encode()
        with patch('urllib.request.urlopen',return_value=response) as request:
            result=JevClient(api_key='synthetic-test-key').classify_file('01_orbe.csv','id_transacao;valor_bruto')
            return result,request.call_args.args[0]
    def test_schema_oficial_e_interpretacao_da_resposta(self):
        result,request=self.call(self.response())
        payload=json.loads(request.data)
        self.assertIn('state',payload)
        self.assertNotIn('context',payload)
        self.assertIn('criteria',payload['questions']['pipeline_domain'])
        self.assertIn('instructions',payload['questions']['pipeline_domain'])
        self.assertEqual(result['domain'],'ORBE_FECHAMENTO_PRINCIPAL')
        self.assertEqual(result['confidence'],0.99)
        self.assertEqual(result['model'],'jev-1.13.0')
    def test_noul_baixo_nao_e_convertido_em_true(self):
        result,_=self.call(self.response(noul=0.1))
        self.assertFalse(result['is_delayed_batch'])
        self.assertEqual(result['delayed_prob'],0.1)
    def test_noul_alto_identifica_complemento(self):
        result,_=self.call(self.response(noul=0.9,domain='ORBE_AJUSTES_TARDIOS'))
        self.assertTrue(result['is_delayed_batch'])
    def test_dominio_fora_do_contrato_nao_e_aceito(self):
        result,_=self.call(self.response(domain='FORA_DO_SCHEMA'))
        self.assertIsNone(result)
    def test_confianca_invalida_nao_e_aceita(self):
        for value in (-1,2,float('nan')):
            with self.subTest(value=value):
                result,_=self.call(self.response(confidence=value))
                self.assertIsNone(result)
    def test_resposta_incompleta_nao_inventa_confianca(self):
        result,_=self.call({'answers':{}})
        self.assertIsNone(result)
