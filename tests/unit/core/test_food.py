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
