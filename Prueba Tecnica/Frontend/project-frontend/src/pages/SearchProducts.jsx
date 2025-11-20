import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  TextInput,
  Grid,
  Card,
  Image,
  Text,
  Badge,
  Button,
  Group,
  Stack,
  Title,
  Select,
  RingProgress,
  Center,
  Loader,
} from '@mantine/core';
import { IconSearch, IconFilter } from '@tabler/icons-react';
import { getProducts, searchProducts } from '../services/api';
import { notifications } from '@mantine/notifications';

function SearchProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('');

  useEffect(() => {
    fetchProducts();
  }, [category]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (category) params.category = category;

      const data = await getProducts(params);
      setProducts(data.results || data);
    } catch (error) {
      console.error('Error al cargar productos:', error);
      notifications.show({
        title: 'Error',
        message: 'No se pudieron cargar los productos',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      fetchProducts();
      return;
    }

    setLoading(true);
    try {
      const data = await searchProducts(searchQuery);
      setProducts(data.results || []);
    } catch (error) {
      console.error('Error en búsqueda:', error);
      notifications.show({
        title: 'Error',
        message: 'Error al buscar productos',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'blue';
    if (score >= 40) return 'yellow';
    return 'red';
  };

  return (
    <Stack gap="md">
      <Title order={1}>Buscar Productos</Title>

      {/* Barra de búsqueda y filtros */}
      <Card shadow="sm" padding="md" radius="md" withBorder>
        <form onSubmit={handleSearch}>
          <Grid>
            <Grid.Col span={{ base: 12, md: 8 }}>
              <TextInput
                placeholder="Buscar productos por nombre, marca o categoría..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftSection={<IconSearch size={16} />}
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Select
                placeholder="Filtrar por categoría"
                leftSection={<IconFilter size={16} />}
                value={category}
                onChange={setCategory}
                data={[
                  { value: '', label: 'Todas las categorías' },
                  { value: 'granos', label: 'Granos y Cereales' },
                  { value: 'lacteos', label: 'Lácteos' },
                  { value: 'carnes', label: 'Carnes y Proteínas' },
                  { value: 'frutas', label: 'Frutas y Verduras' },
                  { value: 'bebidas', label: 'Bebidas' },
                  { value: 'snacks', label: 'Snacks' },
                  { value: 'panaderia', label: 'Panadería' },
                  { value: 'otros', label: 'Otros' },
                ]}
                clearable
                size="md"
              />
            </Grid.Col>
          </Grid>
        </form>
      </Card>

      {/* Resultados */}
      {loading ? (
        <Center h={300}>
          <Loader size="lg" color="green" />
        </Center>
      ) : (
        <>
          <Text c="dimmed">
            {products.length} producto{products.length !== 1 ? 's' : ''}{' '}
            encontrado{products.length !== 1 ? 's' : ''}
          </Text>

          <Grid>
            {products.map((product) => (
              <Grid.Col key={product.id} span={{ base: 12, sm: 6, md: 4, lg: 3 }}>
                <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
                  <Card.Section>
                    <Image
                      src={product.image_url || 'https://via.placeholder.com/200'}
                      height={160}
                      alt={product.name}
                      fallbackSrc="https://via.placeholder.com/200x160?text=Sin+Imagen"
                    />
                  </Card.Section>

                  <Stack gap="xs" mt="md">
                    <Text fw={500} lineClamp={2} size="sm">
                      {product.name}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {product.brand}
                    </Text>

                    <Group gap="xs">
                      {product.nutriscore && (
                        <Badge size="xs" variant="filled" color="blue">
                          Nutri: {product.nutriscore}
                        </Badge>
                      )}
                      {product.ecoscore && (
                        <Badge size="xs" variant="filled" color="green">
                          Eco: {product.ecoscore}
                        </Badge>
                      )}
                    </Group>

                    {product.sustainability_score !== null && (
                      <Center>
                        <RingProgress
                          size={80}
                          thickness={8}
                          sections={[
                            {
                              value: product.sustainability_score,
                              color: getScoreColor(product.sustainability_score),
                            },
                          ]}
                          label={
                            <Center>
                              <Text size="xs" fw={700}>
                                {product.sustainability_score.toFixed(0)}
                              </Text>
                            </Center>
                          }
                        />
                      </Center>
                    )}

                    <Text size="lg" fw={700} c="green">
                      ${product.price}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {product.weight}g
                    </Text>

                    <Button
                      component={Link}
                      to={`/product/${product.id}`}
                      variant="light"
                      color="green"
                      fullWidth
                      mt="xs"
                    >
                      Ver Detalles
                    </Button>
                  </Stack>
                </Card>
              </Grid.Col>
            ))}
          </Grid>

          {products.length === 0 && (
            <Center h={200}>
              <Stack align="center" gap="md">
                <IconSearch size={48} color="#ccc" />
                <Text c="dimmed">No se encontraron productos</Text>
              </Stack>
            </Center>
          )}
        </>
      )}
    </Stack>
  );
}

export default SearchProducts;