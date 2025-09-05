from cwg_llm_openai import ask, ask_from_prompt, save_embedding, ask_from_url, ask_from_pdf, ask_from_embedding


# #Simples
resposta = ask('Quem é Carlos W. Gama?')

# #Contexto
# contexto = 'Carlos W. Gama é um programador'
# resposta = ask_from_prompt('Quem é Carlos W. Gama?', contexto)

# #URL
# url = 'https://carloswgama.com.br';
# resposta = ask_from_url('Quem é Carlos W. Gama?', url);

# #PDF
# caminho_pdf = './src/example/doc.pdf'
# resposta = ask_from_pdf('Quem é Carlos W. Gama?', caminho_pdf)

# # #RAG
# arquivoRAG = 'nome_indice'
# url = 'https://carloswgama.com.br'
# save_embedding(url, rag=arquivoRAG)

# resposta = ask_from_embedding('Quem é Carlos W. Gama?', arquivoRAG)


print(resposta)

