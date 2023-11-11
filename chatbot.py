import spacy

from chatterbot import ChatBot


# from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer


# def train_bot(chatbot):
#     trainer = ListTrainer(chatbot)
#     trainer.train([
#         "Hi",
#         "Welcome, friend 🤗",
#     ])
#     trainer.train([
#         "Are you a plant?",
#         "No, I'm the pot below the plant!",
#     ])
#
#     return chatbot
#
#
# # train chatbot with corpus
# def train_bot_corpus(chatbot):
#     corpus_trainer = ChatterBotCorpusTrainer(chatbot)
#     corpus_trainer.train("chatterbot.corpus.english")
#
#     return chatbot
#
#
# def train_chatbot_with_custom_corpus(chatbot):
#     print("Training chatbot with custom corpus")
#     corpus_trainer = ChatterBotCorpusTrainer(chatbot)
#     corpus_trainer.train("chatterbot.corpus")
#     print("Training chatbot with custom corpus done")
#
#     return chatbot


def initialize_bot():
    try:
        nlp = spacy.load("en_core_web_md")
    except:
        spacy.cli.download("en_core_web_md")
        nlp = spacy.load("en_core_web_md")

    chatbot = ChatBot("HistoMind")

    # train = False
    #
    # if train:
    #     # chatbot = train_bot(chatbot)
    #     # chatbot = train_bot_corpus(chatbot)
    #     chatbot = train_chatbot_with_custom_corpus(chatbot)

    exit_conditions = (":q", "quit", "exit")

    return chatbot, exit_conditions


def get_response_chatbot(query, chatbot):
    print("query: ", query)
    k = chatbot.get_response(query)
    return chatbot.get_response(query)

#
# if __name__ == "__main__":
#     chatbot, exit_conditions = initialize_bot()
#     # print("Bot initialized")
#     # chatbot = train_bot_corpus(chatbot)
#     # print("Bot trained")
#     while True:
#         query = input("> ")
#         if query in exit_conditions:
#             break
#         else:
#             print(f"🪴 {chatbot.get_response(query)}")
