import { useEffect, useState } from 'react';
import {
  Card,
  Text,
  Grid,
  Stack,
  Title,
  Center,
  Loader,
  Badge,
  Group,
  RingProgress,
} from '@mantine/core';
import {
  IconShoppingCart,
  IconChartBar,
  IconCoin,
  IconLeaf,
} from '@tabler/icons-react';
import { BarChart } from '@mantine/charts';
import { getStats } from '../services/api';
import { notifications } from '@mantine/notifications';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
      notifications.show({
        title: 'Error',
        message: 'No se pudieron cargar las estadísticas',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Center h={400}>
        <Loader size="lg" color="green" />
      </Center>
    );
  }

  if (!stats) {
    return (
      <Center h={400}>
        <Text>No se pudieron cargar las estadísticas</Text>
      </Center>
    );
  }

  const categoryData = stats.products_by_category.map((cat) => ({
    category: cat.category,
    productos: cat.count,
  }));

  return (
    <Stack gap="xl">
      <Title order={1}>Dashboard de Estadísticas</Title>

      {/* Cards de estadísticas principales */}
      <Grid>
        <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Text size="sm" c="dimmed">
                Total Productos
              </Text>
              <IconShoppingCart size={24} color="#4caf50" />
            </Group>
            <Title order={2} c="green">
              {stats.total_products}
            </Title>
            <Text size="xs" c="dimmed" mt="xs">
              Productos en la base de datos
            </Text>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Text size="sm" c="dimmed">
                Score Promedio
              </Text>
              <IconChartBar size={24} color="#4caf50" />
            </Group>
            <Title order={2} c="green">
              {stats.sustainability_stats.avg_total?.toFixed(1)}
            </Title>
            <Text size="xs" c="dimmed" mt="xs">
              Puntuación de sostenibilidad
            </Text>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Text size="sm" c="dimmed">
                Precio Promedio
              </Text>
              <IconCoin size={24} color="#4caf50" />
            </Group>
            <Title order={2} c="green">
              ${stats.price_stats.avg_price?.toFixed(0)}
            </Title>
            <Text size="xs" c="dimmed" mt="xs">
              Precio promedio en CLP
            </Text>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Text size="sm" c="dimmed">
                Rango de Precios
              </Text>
              <IconLeaf size={24} color="#4caf50" />
            </Group>
            <Text size="lg" fw={700} c="green">
              ${stats.price_stats.min_price} - ${stats.price_stats.max_price}
            </Text>
            <Text size="xs" c="dimmed" mt="xs">
              Mínimo y máximo
            </Text>
          </Card>
        </Grid.Col>
      </Grid>

      {/* Scores Promedio */}
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={3} mb="md">
          Scores de Sostenibilidad Promedio
        </Title>
        <Grid>
          <Grid.Col span={{ base: 12, md: 3 }}>
            <Center>
              <Stack align="center">
                <Text size="sm" fw={500}>
                  Económico
                </Text>
                <RingProgress
                  size={140}
                  thickness={14}
                  sections={[
                    {
                      value: stats.sustainability_stats.avg_economic || 0,
                      color: 'blue',
                    },
                  ]}
                  label={
                    <Center>
                      <Text size="lg" fw={700}>
                        {stats.sustainability_stats.avg_economic?.toFixed(1)}
                      </Text>
                    </Center>
                  }
                />
              </Stack>
            </Center>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 3 }}>
            <Center>
              <Stack align="center">
                <Text size="sm" fw={500}>
                  Ambiental
                </Text>
                <RingProgress
                  size={140}
                  thickness={14}
                  sections={[
                    {
                      value: stats.sustainability_stats.avg_environmental || 0,
                      color: 'green',
                    },
                  ]}
                  label={
                    <Center>
                      <Text size="lg" fw={700}>
                        {stats.sustainability_stats.avg_environmental?.toFixed(1)}
                      </Text>
                    </Center>
                  }
                />
              </Stack>
            </Center>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 3 }}>
            <Center>
              <Stack align="center">
                <Text size="sm" fw={500}>
                  Social
                </Text>
                <RingProgress
                  size={140}
                  thickness={14}
                  sections={[
                    {
                      value: stats.sustainability_stats.avg_social || 0,
                      color: 'orange',
                    },
                  ]}
                  label={
                    <Center>
                      <Text size="lg" fw={700}>
                        {stats.sustainability_stats.avg_social?.toFixed(1)}
                      </Text>
                    </Center>
                  }
                />
              </Stack>
            </Center>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 3 }}>
            <Center>
              <Stack align="center">
                <Text size="sm" fw={500}>
                  Total
                </Text>
                <RingProgress
                  size={140}
                  thickness={14}
                  sections={[
                    {
                      value: stats.sustainability_stats.avg_total || 0,
                      color: 'teal',
                    },
                  ]}
                  label={
                    <Center>
                      <Text size="lg" fw={700}>
                        {stats.sustainability_stats.avg_total?.toFixed(1)}
                      </Text>
                    </Center>
                  }
                />
              </Stack>
            </Center>
          </Grid.Col>
        </Grid>
      </Card>

      {/* Gráfico de productos por categoría */}
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={3} mb="md">
          Productos por Categoría
        </Title>
        <BarChart
          h={300}
          data={categoryData}
          dataKey="category"
          series={[{ name: 'productos', color: 'green' }]}
          tickLine="y"
          gridAxis="y"
        />
      </Card>

      {/* Categorías en badges */}
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={3} mb="md">
          Todas las Categorías
        </Title>
        <Group>
          {stats.products_by_category.map((cat) => (
            <Badge key={cat.category} size="lg" variant="light" color="green">
              {cat.category}: {cat.count} productos
            </Badge>
          ))}
        </Group>
      </Card>
    </Stack>
  );
}

export default Dashboard;