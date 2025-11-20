import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Title,
  Text,
  Button,
  Grid,
  Card,
  Group,
  Stack,
  Badge,
  Loader,
  Center,
} from '@mantine/core';
import {
  IconLeaf,
  IconShoppingCart,
  IconChartBar,
  IconSearch,
  IconSparkles,
} from '@tabler/icons-react';
import { getStats } from '../services/api';

function Home() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (error) {
        console.error('Error al cargar estadísticas:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <Center h={400}>
        <Loader size="lg" color="green" />
      </Center>
    );
  }

  return (
    <Stack gap="xl">
      {/* Hero Section */}
      <Card shadow="sm" padding="xl" radius="md" withBorder>
        <Stack align="center" gap="md">
          <IconLeaf size={64} color="#4caf50" />
          <Title order={1} ta="center">
            Bienvenido a LiquiVerde
          </Title>
          <Text size="lg" ta="center" c="dimmed" maw={600}>
            Tu plataforma inteligente para ahorrar dinero mientras tomas
            decisiones de compra sostenibles. Optimiza tu presupuesto y reduce
            tu impacto ambiental.
          </Text>

          <Group mt="md">
            <Button
              component={Link}
              to="/search"
              size="lg"
              leftSection={<IconSearch size={20} />}
            >
              Buscar Productos
            </Button>
            <Button
              component={Link}
              to="/optimize"
              size="lg"
              variant="light"
              leftSection={<IconShoppingCart size={20} />}
            >
              Optimizar Lista
            </Button>
          </Group>
        </Stack>
      </Card>

      {/* Estadísticas */}
      <Grid>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Total de Productos</Text>
              <IconShoppingCart size={24} color="#4caf50" />
            </Group>
            <Title order={2} c="green">
              {stats?.total_products || 0}
            </Title>
            <Text size="sm" c="dimmed" mt="xs">
              Productos disponibles en la base de datos
            </Text>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Score Promedio</Text>
              <IconChartBar size={24} color="#4caf50" />
            </Group>
            <Title order={2} c="green">
              {stats?.sustainability_stats?.avg_total?.toFixed(1) || 0}
            </Title>
            <Text size="sm" c="dimmed" mt="xs">
              Puntuación de sostenibilidad promedio
            </Text>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Precio Promedio</Text>
              <IconSparkles size={24} color="#4caf50" />
            </Group>
            <Title order={2} c="green">
              ${stats?.price_stats?.avg_price?.toFixed(0) || 0}
            </Title>
            <Text size="sm" c="dimmed" mt="xs">
              CLP - Precio promedio de productos
            </Text>
          </Card>
        </Grid.Col>
      </Grid>

      {/* Features */}
      <Title order={2} mt="xl">
        ¿Qué puedes hacer?
      </Title>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
            <IconSearch size={32} color="#4caf50" />
            <Title order={3} mt="md">
              Buscar Productos
            </Title>
            <Text size="sm" c="dimmed" mt="xs">
              Explora nuestro catálogo de productos chilenos con información
              detallada sobre sostenibilidad, precios y certificaciones.
            </Text>
            <Button
              component={Link}
              to="/search"
              variant="light"
              mt="md"
              fullWidth
            >
              Ir a Búsqueda
            </Button>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
            <IconShoppingCart size={32} color="#4caf50" />
            <Title order={3} mt="md">
              Optimizar Lista de Compras
            </Title>
            <Text size="sm" c="dimmed" mt="xs">
              Usa nuestro algoritmo inteligente para optimizar tu lista de
              compras según tu presupuesto, maximizando sostenibilidad y ahorro.
            </Text>
            <Button
              component={Link}
              to="/optimize"
              variant="light"
              mt="md"
              fullWidth
            >
              Optimizar Ahora
            </Button>
          </Card>
        </Grid.Col>
      </Grid>

      {/* Categorías Populares */}
      {stats?.products_by_category && (
        <>
          <Title order={2} mt="xl">
            Categorías Populares
          </Title>
          <Group>
            {stats.products_by_category.slice(0, 6).map((cat) => (
              <Badge key={cat.category} size="lg" variant="light" color="green">
                {cat.category}: {cat.count}
              </Badge>
            ))}
          </Group>
        </>
      )}
    </Stack>
  );
}

export default Home;