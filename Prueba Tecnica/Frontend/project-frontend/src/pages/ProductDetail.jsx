import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Card,
  Image,
  Text,
  Badge,
  Button,
  Group,
  Stack,
  Title,
  Grid,
  RingProgress,
  Center,
  Loader,
  Progress,
  Divider,
} from '@mantine/core';
import { IconArrowLeft, IconLeaf, IconCertificate } from '@tabler/icons-react';
import { getProduct, getProductAlternatives } from '../services/api';
import { notifications } from '@mantine/notifications';

function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProductData();
  }, [id]);

  const fetchProductData = async () => {
    setLoading(true);
    try {
      const [productData, alternativesData] = await Promise.all([
        getProduct(id),
        getProductAlternatives(id),
      ]);
      setProduct(productData);
      setAlternatives(alternativesData.alternatives || []);
    } catch (error) {
      console.error('Error al cargar producto:', error);
      notifications.show({
        title: 'Error',
        message: 'No se pudo cargar el producto',
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

  if (loading) {
    return (
      <Center h={400}>
        <Loader size="lg" color="green" />
      </Center>
    );
  }

  if (!product) {
    return (
      <Center h={400}>
        <Text>Producto no encontrado</Text>
      </Center>
    );
  }

  const sustainability = product.sustainability || {};

  return (
    <Stack gap="xl">
      <Button
        component={Link}
        to="/search"
        variant="subtle"
        leftSection={<IconArrowLeft size={16} />}
      >
        Volver a la búsqueda
      </Button>

      <Grid>
        <Grid.Col span={{ base: 12, md: 5 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Image
              src={product.image_url || 'https://via.placeholder.com/400'}
              height={400}
              alt={product.name}
              fallbackSrc="https://via.placeholder.com/400x400?text=Sin+Imagen"
            />
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 7 }}>
          <Stack gap="md">
            <Title order={1}>{product.name}</Title>
            <Text size="lg" c="dimmed">
              {product.brand}
            </Text>

            <Group>
              <Text size="xl" fw={700} c="green">
                ${product.price}
              </Text>
              <Text c="dimmed">
                ({product.weight}{product.unit}) - $
                {product.price_per_unit?.toFixed(2)}/{product.unit}
              </Text>
            </Group>

            <Group>
              {product.nutriscore && (
                <Badge size="lg" variant="filled" color="blue">
                  Nutri-Score: {product.nutriscore}
                </Badge>
              )}
              {product.ecoscore && (
                <Badge size="lg" variant="filled" color="green">
                  Eco-Score: {product.ecoscore}
                </Badge>
              )}
              {product.is_organic && (
                <Badge
                  size="lg"
                  variant="filled"
                  color="teal"
                  leftSection={<IconLeaf size={14} />}
                >
                  Orgánico
                </Badge>
              )}
              {product.is_fairtrade && (
                <Badge
                  size="lg"
                  variant="filled"
                  color="orange"
                  leftSection={<IconCertificate size={14} />}
                >
                  Comercio Justo
                </Badge>
              )}
              {product.is_local && (
                <Badge size="lg" variant="filled" color="violet">
                  Producción Local
                </Badge>
              )}
            </Group>

            <Divider />

            <Text size="sm">
              <strong>Origen:</strong> {product.origin}
            </Text>
            <Text size="sm">
              <strong>Categoría:</strong> {product.category}
            </Text>

            {product.description && (
              <>
                <Divider />
                <Text size="sm">{product.description}</Text>
              </>
            )}
          </Stack>
        </Grid.Col>
      </Grid>

      {/* Scores de Sostenibilidad */}
      {sustainability.total_score !== undefined && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Title order={2} mb="md">
            Puntuación de Sostenibilidad
          </Title>

          <Grid>
            <Grid.Col span={{ base: 12, md: 3 }}>
              <Center>
                <Stack align="center">
                  <Text size="sm" fw={500}>
                    Score Total
                  </Text>
                  <RingProgress
                    size={150}
                    thickness={16}
                    sections={[
                      {
                        value: sustainability.total_score,
                        color: getScoreColor(sustainability.total_score),
                      },
                    ]}
                    label={
                      <Center>
                        <Text size="xl" fw={700}>
                          {sustainability.total_score.toFixed(1)}
                        </Text>
                      </Center>
                    }
                  />
                </Stack>
              </Center>
            </Grid.Col>

            <Grid.Col span={{ base: 12, md: 9 }}>
              <Stack gap="md">
                <div>
                  <Group justify="space-between" mb={5}>
                    <Text size="sm" fw={500}>
                      Score Económico
                    </Text>
                    <Text size="sm" fw={700} c={getScoreColor(sustainability.economic_score)}>
                      {sustainability.economic_score.toFixed(1)}
                    </Text>
                  </Group>
                  <Progress
                    value={sustainability.economic_score}
                    color={getScoreColor(sustainability.economic_score)}
                    size="lg"
                  />
                  <Text size="xs" c="dimmed" mt={5}>
                    Relación precio/calidad (menor precio = mejor score)
                  </Text>
                </div>

                <div>
                  <Group justify="space-between" mb={5}>
                    <Text size="sm" fw={500}>
                      Score Ambiental
                    </Text>
                    <Text
                      size="sm"
                      fw={700}
                      c={getScoreColor(sustainability.environmental_score)}
                    >
                      {sustainability.environmental_score.toFixed(1)}
                    </Text>
                  </Group>
                  <Progress
                    value={sustainability.environmental_score}
                    color={getScoreColor(sustainability.environmental_score)}
                    size="lg"
                  />
                  <Text size="xs" c="dimmed" mt={5}>
                    Basado en Nutri-Score, Eco-Score y certificaciones
                  </Text>
                </div>

                <div>
                  <Group justify="space-between" mb={5}>
                    <Text size="sm" fw={500}>
                      Score Social
                    </Text>
                    <Text size="sm" fw={700} c={getScoreColor(sustainability.social_score)}>
                      {sustainability.social_score.toFixed(1)}
                    </Text>
                  </Group>
                  <Progress
                    value={sustainability.social_score}
                    color={getScoreColor(sustainability.social_score)}
                    size="lg"
                  />
                  <Text size="xs" c="dimmed" mt={5}>
                    Comercio justo, producción local y origen
                  </Text>
                </div>
              </Stack>
            </Grid.Col>
          </Grid>
        </Card>
      )}

      {/* Productos Alternativos */}
      {alternatives.length > 0 && (
        <>
          <Title order={2}>Alternativas Recomendadas</Title>
          <Grid>
            {alternatives.map((alt) => (
              <Grid.Col key={alt.id} span={{ base: 12, sm: 6, md: 4 }}>
                <Card shadow="sm" padding="md" radius="md" withBorder h="100%">
                  <Card.Section>
                    <Image
                      src={alt.image_url || 'https://via.placeholder.com/200'}
                      height={120}
                      alt={alt.name}
                      fallbackSrc="https://via.placeholder.com/200x120?text=Sin+Imagen"
                    />
                  </Card.Section>

                  <Stack gap="xs" mt="md">
                    <Text fw={500} lineClamp={2} size="sm">
                      {alt.name}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {alt.brand}
                    </Text>
                    <Text size="md" fw={700} c="green">
                      ${alt.price}
                    </Text>

                    {alt.sustainability_score !== null && (
                      <Badge color={getScoreColor(alt.sustainability_score)}>
                        Score: {alt.sustainability_score.toFixed(0)}
                      </Badge>
                    )}

                    <Button
                      component={Link}
                      to={`/product/${alt.id}`}
                      variant="light"
                      size="xs"
                      fullWidth
                    >
                      Ver Detalles
                    </Button>
                  </Stack>
                </Card>
              </Grid.Col>
            ))}
          </Grid>
        </>
      )}
    </Stack>
  );
}

export default ProductDetail;