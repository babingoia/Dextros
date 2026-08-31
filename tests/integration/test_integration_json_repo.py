import pytest
import json
from uuid import uuid4
from datetime import date, time
from pathlib import Path

# --- Imports do seu projeto ---
# Ajuste os caminhos de importação conforme a estrutura real do seu projeto
from adapters.repositories.jsonRepo import JsonRepository
from frameworks.json_handler_service import JsonHandler
from adapters.parsers.card_data_model_parser import CardDataModelParser
from usecases.Factories.card_creator import CardCreator 
from adapters.exceptions import CardNotFoundError

# Imports dos Value Objects para criar dados de teste
from core.value_objects.card_id import CardID
from core.value_objects.date import Date
from core.value_objects.time import Time
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.exercise import Exercise
from core.value_objects.meal import MealPeriod
from core.value_objects.observation import Observation
from core.value_objects.card import Card


# ==========================================
# HELPERS E FIXTURES
# ==========================================

def make_dummy_card(card_id: str = None, glycemia: int = 120, obs: str = "Observação de teste") -> Card:
    """Função auxiliar para criar um Card válido rapidamente para os testes."""
    cid = CardID.parse(card_id or str(uuid4()))
    # Usa a data de hoje para não cair no ValueError do __post_init__ do Card (data futura)
    cdate = Date.parse(date.today()) 
    ctime = Time.parse(time(14, 30))
    cglyc = Glycemia.parse(glycemia)
    clong = LongActingInsulin.parse(10)
    cshort = ShortActingInsulin.parse(5)
    cexer = Exercise.parse("Corrida", "moderada")
    cmeal = MealPeriod.parse("pré almoço")
    cobs = Observation.parse(obs)
    
    return Card(cid, cdate, ctime, cglyc, clong, cshort, cexer, cmeal, cobs)


@pytest.fixture
def json_handler(tmp_path):
    """Cria um JsonHandler apontando para um arquivo temporário."""
    file_path = tmp_path / "test_cards.json"
    return JsonHandler(save_path=file_path)

@pytest.fixture
def parser():
    return CardDataModelParser()

@pytest.fixture
def creator():
    return CardCreator()

@pytest.fixture
def repository(json_handler, parser, creator):
    """Instancia o JsonRepository com dependências reais."""
    return JsonRepository(handler=json_handler, card_creator=creator, parser=parser)


# ==========================================
# TESTES DE INICIALIZAÇÃO (LOAD)
# ==========================================

def test_init_with_no_file(repository):
    """Se o arquivo não existir, deve inicializar com lista vazia sem erro."""
    cards = repository.get_all_cards()
    assert cards == []

def test_init_with_existing_valid_data(json_handler, parser, creator, tmp_path):
    """Se o arquivo já existir com dados, deve carregar corretamente."""
    # 1. Prepara um JSON válido manualmente
    dummy_card = make_dummy_card(card_id="f47ac10b-58cc-4372-a567-0e02b2c3d479", glycemia=150)
    
    # Simula o que o handler faria para criar o arquivo
    handler_for_setup = JsonHandler(save_path=tmp_path / "test_cards.json")
    # Precisamos mapear para o TypedDict manualmente aqui para o setup
    data_model = {
        "card_id": str(dummy_card.card_id.card_id),
        "card_date": dummy_card.card_date._date.isoformat(),
        "card_time": dummy_card.card_time._time.strftime("%H:%M"),
        "glycemia": dummy_card.glycemia.glycemia,
        "long_acting_insulin": dummy_card.long_acting_insulin.quantity,
        "short_acting_insulin": dummy_card.short_acting_insulin.quantity,
        "meal": dummy_card.meal.meal_period,
        "observation": dummy_card.obs.observation,
        "exercise": {
            "exercise_name": dummy_card.exercise.exercise_name,
            "intensity": dummy_card.exercise.intensity
        }
    }
    handler_for_setup.export([data_model])

    # 2. Inicializa o repositório
    repo = JsonRepository(handler=json_handler, card_creator=creator, parser=parser)
    
    # 3. Verifica se carregou
    cards = repo.get_all_cards()
    assert len(cards) == 1
    assert cards[0].glycemia.glycemia == 150

def test_init_with_corrupted_json(json_handler, parser, creator, tmp_path):
    """Se o JSON estiver corrompido, deve levantar JSONDecodeError na inicialização."""
    file_path = tmp_path / "test_cards.json"
    file_path.write_text("{isso nao eh um json valido: [}", encoding="utf-8")
    
    with pytest.raises(json.JSONDecodeError):
        JsonRepository(handler=json_handler, card_creator=creator, parser=parser)


# ==========================================
# TESTES DE CRUD (ADD, GET, UPDATE, REMOVE)
# ==========================================

def test_add_card_and_persist(repository, json_handler):
    """Adicionar um card deve salvar no disco e recuperar corretamente."""
    card = make_dummy_card()
    repository.add_card(card)
    
    # Verifica na memória
    assert len(repository.get_all_cards()) == 1
    
    # Verifica no disco (lendo o JSON cru)
    with open(json_handler.save_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    assert len(raw_data["cards"]) == 1
    assert raw_data["cards"][0]["card_id"] == str(card.card_id.card_id)

def test_get_card_success(repository):
    """Deve retornar o card correto ao buscar por um ID existente."""
    card1 = make_dummy_card()
    card2 = make_dummy_card()
    repository.add_card(card1)
    repository.add_card(card2)
    
    found_card = repository.get_card(str(card2.card_id.card_id))
    assert found_card.card_id == card2.card_id

def test_get_card_not_found(repository):
    """Deve levantar CardNotFoundError ao buscar um ID inexistente."""
    with pytest.raises(CardNotFoundError):
        repository.get_card("00000000-0000-0000-0000-000000000000")

def test_remove_card_success(repository):
    """Deve remover o card da memória e do disco."""
    card = make_dummy_card()
    repository.add_card(card)
    assert len(repository.get_all_cards()) == 1
    
    repository.remove_card(str(card.card_id.card_id))
    
    assert len(repository.get_all_cards()) == 0

def test_remove_card_not_found(repository):
    """Deve levantar CardNotFoundError ao tentar remover um ID inexistente."""
    # Adiciona um card qualquer para garantir que a lista não está vazia
    repository.add_card(make_dummy_card())
    
    with pytest.raises(CardNotFoundError):
        repository.remove_card("00000000-0000-0000-0000-000000000000")

def test_update_card_success(repository):
    """Deve atualizar o card existente e persistir a mudança."""
    original_card = make_dummy_card(glycemia=100)
    repository.add_card(original_card)
    
    # Cria um novo card com o MESMO ID, mas glicemia diferente
    updated_card = make_dummy_card(
        card_id=str(original_card.card_id.card_id), 
        glycemia=200
    )
    repository.update_card(updated_card)
    
    # Verifica na memória
    cards = repository.get_all_cards()
    assert len(cards) == 1
    assert cards[0].glycemia.glycemia == 200
    
    # Verifica no disco
    found = repository.get_card(str(original_card.card_id.card_id))
    assert found.glycemia.glycemia == 200

def test_update_card_not_found(repository):
    """Deve levantar CardNotFoundError ao tentar atualizar um ID inexistente."""
    fake_card = make_dummy_card()
    
    with pytest.raises(CardNotFoundError):
        repository.update_card(fake_card)


# ==========================================
# TESTES DE CASOS DE BORDA E ARQUITETURA
# ==========================================

def test_special_characters_are_saved_correctly(repository, json_handler):
    """
    Garante que o ensure_ascii=False está funcionando.
    Se não estiver, emojis e acentos viram códigos unicode escapados no JSON.
    """
    card = make_dummy_card(obs="Teste com acentuação: é, ã, ç e emoji 🚀")
    repository.add_card(card)
    
    # Lê o arquivo como texto cru para verificar a formatação
    raw_text = json_handler.save_path.read_text(encoding="utf-8")
    
    # O texto cru DEVE conter o emoji e os acentos diretamente, não unicode escaped
    assert "🚀" in raw_text
    assert "acentuação" in raw_text
    assert "\\u" not in raw_text # Garante que não houve escape

def test_multiple_operations_maintain_consistency(repository):
    """Teste de estresse: várias adições, remoções e updates para garantir que a lista não corrompe."""
    cards = [make_dummy_card() for _ in range(5)]
    
    for c in cards:
        repository.add_card(c)
    assert len(repository.get_all_cards()) == 5
    
    # Remove o do meio
    repository.remove_card(str(cards[2].card_id.card_id))
    assert len(repository.get_all_cards()) == 4
    
    # Atualiza o último
    updated_last = make_dummy_card(
        card_id=str(cards[4].card_id.card_id), 
        glycemia=300
    )
    repository.update_card(updated_last)
    
    # Verifica integridade final
    final_cards = repository.get_all_cards()
    assert len(final_cards) == 4
    assert any(c.glycemia.glycemia == 300 for c in final_cards)
    assert not any(str(c.card_id.card_id) == str(cards[2].card_id.card_id) for c in final_cards)