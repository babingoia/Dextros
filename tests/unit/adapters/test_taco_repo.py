import pytest

from adapters.exceptions import FoodDataError
from adapters.repositories.tacoRepo import TacoRepository, _normalize_taco_value
from core.value_objects.food import Food


TACO_PATH = "db/TACO.json"


@pytest.fixture(scope="module")
def real_repo():
    """A carga real do arquivo é responsabilidade do adapter — aqui o arquivo real é o fixture."""
    return TacoRepository(TACO_PATH)


class TestNormalizeTacoValue:
    @pytest.mark.parametrize("raw,expected", [
        ("NA", None), ("Tr", None), ("", None), (None, None),
        (25.80975, 25.80975), (145, 145.0), ("77.45", 77.45),
    ])
    def test_convencoes_da_fonte(self, raw, expected):
        assert _normalize_taco_value(raw) == expected

    def test_string_imparseavel_vira_none_com_warning(self):
        """Convenção da fonte: valor não confiável = indisponível, nunca zero."""
        assert _normalize_taco_value("não sei") is None

    def test_ruido_negativo_pequeno_vira_zero(self):
        """A TACO real tem 4 carboidratos negativos em peixes/carnes (-0.045 a -0.007),
        ruído de média laboratorial. Analiticamente são zero — nunca chegam ao VO."""
        assert _normalize_taco_value(-0.045) == 0.0
        assert _normalize_taco_value(-0.007) == 0.0

    def test_negativo_grande_e_corrupcao(self):
        from adapters.exceptions import FoodDataError
        with pytest.raises(FoodDataError):
            _normalize_taco_value(-5.0)


class TestTacoRepository:
    def test_carrega_os_597_alimentos(self, real_repo):
        assert len(real_repo.get_all()) == 597

    def test_primeiro_alimento_e_arroz_integral_cozido(self, real_repo):
        arroz = real_repo.get_all()[0]
        assert isinstance(arroz, Food)
        assert arroz.food_id == 1
        assert arroz.description == "Arroz, integral, cozido"
        assert arroz.category == "Cereais e derivados"
        assert arroz.carbohydrate_g == pytest.approx(25.80975)
        assert arroz.fat_g == pytest.approx(1.00033333333333)

    def test_valores_na_da_tabela_viram_none(self, real_repo):
        """~11 alimentos sem carboidrato e ~33 sem gordura confiáveis na TACO."""
        foods = real_repo.get_all()
        sem_carb = [f for f in foods if f.carbohydrate_g is None]
        sem_fat = [f for f in foods if f.fat_g is None]
        assert len(sem_carb) > 0
        assert len(sem_fat) > 0

    def test_cache_nao_rel_o_arquivo(self, real_repo):
        """Segunda chamada devolve os mesmos objetos sem reler."""
        primeira = real_repo.get_all()
        segunda = real_repo.get_all()
        assert primeira == segunda

    def test_get_all_retorna_copia_defensiva(self, real_repo):
        """Mutação da lista retornada não corói o cache do repositório."""
        foods = real_repo.get_all()
        foods.clear()
        assert len(real_repo.get_all()) == 597

    def test_arquivo_inexistente_levanta_food_data_error(self, tmp_path):
        repo = TacoRepository(tmp_path / "não_existe.json")
        with pytest.raises(FoodDataError):
            repo.get_all()

    def test_json_invalido_levanta_food_data_error(self, tmp_path):
        arquivo = tmp_path / "taco.json"
        arquivo.write_text("{não é json", encoding="utf-8")
        repo = TacoRepository(arquivo)
        with pytest.raises(FoodDataError):
            repo.get_all()

    def test_entrada_invalida_levanta_food_data_error_com_contexto(self, tmp_path):
        import json as _json
        arquivo = tmp_path / "taco.json"
        arquivo.write_text(_json.dumps([
            {"id": 1, "description": "   ", "category": "Categoria", "carbohydrate_g": 10}
        ]), encoding="utf-8")
        repo = TacoRepository(arquivo)
        with pytest.raises(FoodDataError, match="id=1"):
            repo.get_all()
