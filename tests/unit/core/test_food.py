import pytest

from core.value_objects.food import Food


class TestFoodParse:
    def test_alimento_completo_da_taco(self):
        resultado = Food.parse(1, "Arroz, integral, cozido", "Cereais e derivados",
                               25.80975, 1.00033333333333)
        assert resultado.food_id == 1
        assert resultado.description == "Arroz, integral, cozido"
        assert resultado.category == "Cereais e derivados"
        assert resultado.carbohydrate_g == pytest.approx(25.80975)
        assert resultado.fat_g == pytest.approx(1.00033333333333)
        assert resultado.energy_kcal is None
        assert resultado.protein_g is None
        assert resultado.fiber_g is None
        assert resultado.sodium_mg is None

    def test_campos_detalhados_do_popup_de_alimento(self):
        """Energia, proteína, fibra e sódio complementam CHO/gordura para o popup
        de detalhes do alimento — mesmas regras por 100g do resto do VO."""
        resultado = Food.parse(1, "Arroz, integral, cozido", "Cereais e derivados",
                               25.80975, 1.00033333333333,
                               energy_value=123.5348925,
                               protein_value=2.58825,
                               fiber_value=2.74933333333333,
                               sodium_value=1.24466666666667)
        assert resultado.energy_kcal == pytest.approx(123.5348925)
        assert resultado.protein_g == pytest.approx(2.58825)
        assert resultado.fiber_g == pytest.approx(2.74933333333333)
        assert resultado.sodium_mg == pytest.approx(1.24466666666667)

    @pytest.mark.parametrize("valor", ["", None])
    def test_campos_detalhados_indisponiveis_viram_none(self, valor):
        resultado = Food.parse(1, "Teste", "Categoria", None, None,
                               energy_value=valor, protein_value=valor,
                               fiber_value=valor, sodium_value=valor)
        assert resultado.energy_kcal is None
        assert resultado.protein_g is None
        assert resultado.fiber_g is None
        assert resultado.sodium_mg is None

    @pytest.mark.parametrize("campo", ["energy_value", "protein_value", "fiber_value", "sodium_value"])
    @pytest.mark.parametrize("valor", [-1, -0.001, float("nan"), float("inf"), object(), True])
    def test_campo_detalhado_invalido_e_rejeitado(self, campo, valor):
        kwargs = {campo: valor}
        with pytest.raises((ValueError, TypeError)):
            Food.parse(1, "Teste", "Categoria", None, None, **kwargs)

    def test_precisao_original_da_tabela_e_preservada(self):
        """Food mantém a precisão da TACO — quem arredonda é o Meal consumido, não a referência."""
        resultado = Food.parse(2, "Arroz, integral, cru", "Cereais e derivados",
                               "77.4507141304348", None)
        assert resultado.carbohydrate_g == pytest.approx(77.4507141304348)
        assert resultado.fat_g is None

    @pytest.mark.parametrize("valor", ["", None])
    def test_valores_indisponiveis_viram_none(self, valor):
        """O VO trata string vazia como indisponível. As convenções da fonte
        ("NA", "Tr") são normalizadas pelo TacoRepository, não aqui — chegar
        até o VO significa erro da fonte."""
        resultado = Food.parse(1, "Teste", "Categoria", valor, valor)
        assert resultado.carbohydrate_g is None
        assert resultado.fat_g is None

    @pytest.mark.parametrize("valor", ["NA", "Tr"])
    def test_convencoes_da_fonte_nao_sao_responsabilidade_do_vo(self, valor):
        """Se 'NA'/'Tr' vazarem até o VO, é bug da fonte de dados: falha ruidosa."""
        with pytest.raises(ValueError):
            Food.parse(1, "Teste", "Categoria", valor, None)

    def test_description_e_category_sao_normalizadas_nas_bordas(self):
        resultado = Food.parse(1, "  Arroz  ", "  Cereais  ")
        assert resultado.description == "Arroz"
        assert resultado.category == "Cereais"

    @pytest.mark.parametrize("campo", ["description", "category"])
    def test_campos_de_exibicao_nao_podem_ser_vazios(self, campo):
        kwargs = {"food_id": 1, "description": "Arroz", "category": "Cereais"}
        kwargs[campo] = "   "
        with pytest.raises(ValueError):
            Food.parse(**kwargs)

    @pytest.mark.parametrize("valor", [-1, -0.001, "-2"])
    def test_valor_nutricional_negativo_e_impossivel(self, valor):
        with pytest.raises(ValueError):
            Food.parse(1, "Teste", "Categoria", valor, None)

    @pytest.mark.parametrize("valor", [float("nan"), float("inf")])
    def test_valor_nao_finito_e_rejeitado(self, valor):
        with pytest.raises(ValueError):
            Food.parse(1, "Teste", "Categoria", valor, None)

    @pytest.mark.parametrize("valor", [object(), [1.0], True])
    def test_tipo_impossivel_e_rejeitado(self, valor):
        with pytest.raises(TypeError):
            Food.parse(1, "Teste", "Categoria", valor, None)

    @pytest.mark.parametrize("campo", ["description", "category"])
    def test_campos_de_exibicao_devem_ser_string(self, campo):
        kwargs = {"food_id": 1, "description": "Arroz", "category": "Cereais"}
        kwargs[campo] = 123
        with pytest.raises(TypeError):
            Food.parse(**kwargs)

    def test_food_id_como_string_numerica_e_aceito(self):
        resultado = Food.parse("1", "Arroz", "Cereais")
        assert resultado.food_id == 1

    def test_food_id_negativo_e_impossivel(self):
        with pytest.raises(ValueError):
            Food.parse(-1, "Arroz", "Cereais")

    def test_e_imutavel(self):
        resultado = Food.parse(1, "Arroz", "Cereais", 25.0, None)
        with pytest.raises(Exception):
            resultado.description = "outro"
