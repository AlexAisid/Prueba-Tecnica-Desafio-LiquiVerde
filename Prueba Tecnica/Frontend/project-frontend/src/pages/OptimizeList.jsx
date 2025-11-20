import { useState, useEffect } from 'react';
import {
  Card,
  Text,
  Button,
  Group,
  Stack,
  Title,
  NumberInput,
  Select,
  Table,
  Badge,
  Alert,
  Grid,
  ActionIcon,
  Divider,
  RingProgress,
  Center,
} from '@mantine/core';
import {
  IconPlus,
  IconTrash,
  IconSparkles,
  IconAlertCircle,
  IconCheck,
  IconChartBar,
} from '@tabler/icons-react';
import { getProducts, optimizeShoppingList } from '../services/api';
import { notifications } from '@mantine/notifications';
import { IconCircleCheck, IconLeaf } from '@tabler/icons-react';

function OptimizeList() {
  const [products, setProducts] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [budget, setBudget] = useState(20000);
  const [optimizedResult, setOptimizedResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data.results || data);
    } catch (error) {
      console.error('Error al cargar productos:', error);
    }
  };

  const addItem = () => {
    setSelectedItems([
      ...selectedItems,
      {
        id: Date.now(),
        product_id: null,
        quantity: 1,
      },
    ]);
  };

  const removeItem = (id) => {
    setSelectedItems(selectedItems.filter((item) => item.id !== id));
  };

  const updateItem = (id, field, value) => {
    setSelectedItems(
      selectedItems.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const handleOptimize = async () => {
    // Validar que todos los items tengan producto seleccionado
    const invalidItems = selectedItems.filter((item) => !item.product_id);
    if (invalidItems.length > 0) {
      notifications.show({
        title: 'Error',
        message: 'Debes seleccionar un producto para cada item',
        color: 'red',
      });
      return;
    }

    if (!budget || budget <= 0) {
      notifications.show({
        title: 'Error',
        message: 'Debes ingresar un presupuesto válido',
        color: 'red',
      });
      return;
    }

    setLoading(true);
    try {
      const items = selectedItems.map((item) => ({
        product_id: parseInt(item.product_id),
        quantity: item.quantity,
      }));

      const result = await optimizeShoppingList(items, budget);
      setOptimizedResult(result);

      notifications.show({
        title: 'Éxito',
        message: '¡Lista optimizada correctamente!',
        color: 'green',
        icon: <IconCheck />,
      });
    } catch (error) {
      console.error('Error al optimizar:', error);
      notifications.show({
        title: 'Error',
        message: 'No se pudo optimizar la lista',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const getProductById = (productId) => {
    return products.find((p) => p.id === parseInt(productId));
  };

  const calculateOriginalTotal = () => {
    return selectedItems.reduce((total, item) => {
      const product = getProductById(item.product_id);
      if (product) {
        return total + parseFloat(product.price) * item.quantity;
      }
      return total;
    }, 0);
  };

  return (
    <Stack gap="xl">
      <Title order={1}>Optimizar Lista de Compras</Title>

      <Alert icon={<IconAlertCircle size={16} />} title="¿Cómo funciona?" color="blue">
        Agrega productos a tu lista y define tu presupuesto. Nuestro algoritmo
        inteligente optimizará tu compra para maximizar la sostenibilidad dentro
        de tu presupuesto.
      </Alert>

      {/* Configuración de presupuesto */}
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={3} mb="md">
          Presupuesto
        </Title>
        <NumberInput
          label="Presupuesto Máximo (CLP)"
          value={budget}
          onChange={setBudget}
          min={0}
          step={1000}
          size="lg"
          leftSection="$"
          thousandSeparator=","
        />
      </Card>

      {/* Lista de productos */}
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Title order={3}>Productos Deseados</Title>
          <Button leftSection={<IconPlus size={16} />} onClick={addItem}>
            Agregar Producto
          </Button>
        </Group>

        {selectedItems.length === 0 ? (
          <Text c="dimmed" ta="center" py="xl">
            No hay productos agregados. Haz clic en "Agregar Producto" para comenzar.
          </Text>
        ) : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Producto</Table.Th>
                <Table.Th>Cantidad</Table.Th>
                <Table.Th>Precio Unit.</Table.Th>
                <Table.Th>Subtotal</Table.Th>
                <Table.Th></Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {selectedItems.map((item) => {
                const product = getProductById(item.product_id);
                const subtotal = product
                  ? parseFloat(product.price) * item.quantity
                  : 0;

                return (
                  <Table.Tr key={item.id}>
                    <Table.Td>
                      <Select
                        placeholder="Seleccionar producto"
                        value={item.product_id?.toString()}
                        onChange={(value) => updateItem(item.id, 'product_id', value)}
                        data={products.map((p) => ({
                          value: p.id.toString(),
                          label: `${p.name} - $${p.price}`,
                        }))}
                        searchable
                      />
                    </Table.Td>
                    <Table.Td>
                      <NumberInput
                        value={item.quantity}
                        onChange={(value) => updateItem(item.id, 'quantity', value)}
                        min={1}
                        style={{ width: 80 }}
                      />
                    </Table.Td>
                    <Table.Td>
                      <Text>{product ? `$${product.price}` : '-'}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text fw={600}>${subtotal.toFixed(0)}</Text>
                    </Table.Td>
                    <Table.Td>
                      <ActionIcon
                        color="red"
                        variant="subtle"
                        onClick={() => removeItem(item.id)}
                      >
                        <IconTrash size={18} />
                      </ActionIcon>
                    </Table.Td>
                  </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        )}

        {selectedItems.length > 0 && (
          <>
            <Divider my="md" />
            <Group justify="space-between">
              <Text fw={600}>Total Original:</Text>
              <Text fw={700} size="lg" c="blue">
                ${calculateOriginalTotal().toFixed(0)}
              </Text>
            </Group>
          </>
        )}
      </Card>

      {/* Botón optimizar */}
      {selectedItems.length > 0 && (
        <Button
          size="lg"
          leftSection={<IconSparkles size={20} />}
          onClick={handleOptimize}
          loading={loading}
          color="green"
        >
          Optimizar Lista
        </Button>
      )}

      {/* Resultados */}
      {optimizedResult && (
        <Card shadow="md" padding="xl" radius="md" withBorder>
          <Stack gap="xl">
            {/* Detectar si no hubo optimización necesaria */}
            {optimizedResult.savings === 0 && optimizedResult.items_removed === 0 ? (
              <>
                {/* ============================================ */}
                {/* CASO 1: NO NECESITA OPTIMIZACIÓN */}
                {/* ============================================ */}

                <Alert
                  icon={<IconCircleCheck size={24} />}
                  title="¡Tu lista está dentro del presupuesto!"
                  color="green"
                  variant="light"
                >
                  <Text size="sm" mb="md">
                    Buenas noticias: El total de tu lista de compras (${optimizedResult.original_total})
                    está dentro de tu presupuesto de ${budget}. No es necesario optimizar ni remover productos.
                  </Text>
                  <Text size="sm" fw={500}>
                    Puedes proceder con tu compra tal como está. ¡Todos los productos que seleccionaste están incluidos!
                  </Text>
                </Alert>

                {/* Estadísticas simplificadas */}
                <Grid>
                  <Grid.Col span={{ base: 12, md: 4 }}>
                    <Card shadow="sm" padding="lg" withBorder h="100%">
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Total de Compra
                        </Text>
                        <Text size="xl" fw={700} c="green">
                          ${optimizedResult.original_total}
                        </Text>
                        <Badge color="green" size="lg">
                          Dentro del presupuesto
                        </Badge>
                      </Stack>
                    </Card>
                  </Grid.Col>

                  <Grid.Col span={{ base: 12, md: 4 }}>
                    <Card shadow="sm" padding="lg" withBorder h="100%">
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Presupuesto Disponible
                        </Text>
                        <Text size="xl" fw={700} c="blue">
                          ${(budget - optimizedResult.original_total).toFixed(0)}
                        </Text>
                        <Text size="xs" c="dimmed">
                          Restante del presupuesto
                        </Text>
                      </Stack>
                    </Card>
                  </Grid.Col>

                  <Grid.Col span={{ base: 12, md: 4 }}>
                    <Card shadow="sm" padding="lg" withBorder h="100%">
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Presupuesto Usado
                        </Text>
                        <RingProgress
                          size={80}
                          thickness={10}
                          sections={[
                            {
                              value: optimizedResult.budget_used_percentage || 0,
                              color: 'green',
                            },
                          ]}
                          label={
                            <Center>
                              <Text size="sm" fw={700}>
                                {(optimizedResult.budget_used_percentage || 0).toFixed(0)}%
                              </Text>
                            </Center>
                          }
                        />
                      </Stack>
                    </Card>
                  </Grid.Col>
                </Grid>

                {/* Lista de productos - CON MANEJO SEGURO DE CAMPOS */}
                <div>
                  <Title order={3} mb="md">
                    Tu Lista de Compras
                  </Title>
                  <Table striped highlightOnHover>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Producto</Table.Th>
                        <Table.Th>Cantidad</Table.Th>
                        <Table.Th>Precio</Table.Th>
                        <Table.Th>Score</Table.Th>
                        <Table.Th>Subtotal</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {optimizedResult.optimized_list.map((item, index) => {
                        // Calcular valores de forma segura
                        const price = typeof item.price === 'number' ? item.price : parseFloat(item.price || 0);
                        const quantity = item.quantity || 0;
                        const subtotal = item.subtotal || (price * quantity);
                        const sustainabilityScore = item.sustainability_score || 0;

                        return (
                          <Table.Tr key={index}>
                            <Table.Td>{item.name || 'N/A'}</Table.Td>
                            <Table.Td>{quantity}</Table.Td>
                            <Table.Td>${price.toFixed(0)}</Table.Td>
                            <Table.Td>
                              <Badge color="green">
                                {sustainabilityScore.toFixed(0)}
                              </Badge>
                            </Table.Td>
                            <Table.Td>
                              <Text fw={600}>${subtotal.toFixed(0)}</Text>
                            </Table.Td>
                          </Table.Tr>
                        );
                      })}
                    </Table.Tbody>
                  </Table>
                </div>

                {/* Info de sostenibilidad */}
                <Card shadow="sm" padding="md" withBorder>
                  <Group justify="space-between">
                    <div>
                      <Text size="sm" c="dimmed">Score de Sostenibilidad Promedio</Text>
                      <Text size="xl" fw={700} c="green">
                        {(optimizedResult.average_score_original || 0).toFixed(1)}
                      </Text>
                    </div>
                    <IconLeaf size={48} color="#4caf50" />
                  </Group>
                </Card>
              </>
            ) : (
              <>
                {/* ============================================ */}
                {/* CASO 2: SÍ NECESITÓ OPTIMIZACIÓN */}
                {/* ============================================ */}

                <Title order={2}>
                  <IconCheck size={28} style={{ marginRight: 8 }} color="green" />
                  Resultados de Optimización
                </Title>

                {/* Estadísticas */}
                <Grid>
                  <Grid.Col span={{ base: 12, md: 3 }}>
                    <Card shadow="sm" padding="lg" withBorder style={{ minHeight: '150px' }}>
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Total Original
                        </Text>
                        <Text size="xl" fw={700}>
                          ${optimizedResult.original_total}
                        </Text>
                      </Stack>
                    </Card>
                  </Grid.Col>

                  <Grid.Col span={{ base: 12, md: 3 }}>
                    <Card shadow="sm" padding="lg" withBorder style={{ minHeight: '150px' }}>
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Total Optimizado
                        </Text>
                        <Text size="xl" fw={700} c="green">
                          ${optimizedResult.optimized_total}
                        </Text>
                      </Stack>
                    </Card>
                  </Grid.Col>

                  <Grid.Col span={{ base: 12, md: 3 }}>
                    <Card shadow="sm" padding="lg" withBorder style={{ minHeight: '150px' }}>
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Ahorro
                        </Text>
                        <Text size="xl" fw={700} c="blue">
                          ${optimizedResult.savings.toFixed(0)}
                        </Text>
                        <Badge color="blue" size="lg">
                          {optimizedResult.savings_percentage.toFixed(1)}% ahorro
                        </Badge>
                      </Stack>
                    </Card>
                  </Grid.Col>

                  <Grid.Col span={{ base: 12, md: 3 }}>
                    <Card shadow="sm" padding="lg" withBorder style={{ minHeight: '150px' }}>
                      <Stack gap="md" align="center" justify="center" h="100%">
                        <Text size="sm" c="dimmed" ta="center">
                          Presupuesto Usado
                        </Text>
                        <RingProgress
                          size={80}
                          thickness={10}
                          sections={[
                            {
                              value: optimizedResult.budget_used_percentage,
                              color:
                                optimizedResult.budget_used_percentage > 90
                                  ? 'red'
                                  : 'green',
                            },
                          ]}
                          label={
                            <Center>
                              <Text size="sm" fw={700}>
                                {optimizedResult.budget_used_percentage.toFixed(0)}%
                              </Text>
                            </Center>
                          }
                        />
                      </Stack>
                    </Card>
                  </Grid.Col>
                </Grid>

                {/* Tabla de productos optimizados - CON MANEJO SEGURO DE CAMPOS */}
                <div>
                  <Title order={3} mb="md">
                    Lista Optimizada
                  </Title>
                  <Table striped highlightOnHover>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Producto</Table.Th>
                        <Table.Th>Cantidad</Table.Th>
                        <Table.Th>Precio</Table.Th>
                        <Table.Th>Score</Table.Th>
                        <Table.Th>Subtotal</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {optimizedResult.optimized_list.map((item, index) => {
                        // Calcular valores de forma segura
                        const price = typeof item.price === 'number' ? item.price : parseFloat(item.price || 0);
                        const quantity = item.quantity || 0;
                        const subtotal = item.subtotal || (price * quantity);
                        const sustainabilityScore = item.sustainability_score || 0;

                        return (
                          <Table.Tr key={index}>
                            <Table.Td>{item.name || 'N/A'}</Table.Td>
                            <Table.Td>{quantity}</Table.Td>
                            <Table.Td>${price.toFixed(0)}</Table.Td>
                            <Table.Td>
                              <Badge color="green">
                                {sustainabilityScore.toFixed(0)}
                              </Badge>
                            </Table.Td>
                            <Table.Td>
                              <Text fw={600}>${subtotal.toFixed(0)}</Text>
                            </Table.Td>
                          </Table.Tr>
                        );
                      })}
                    </Table.Tbody>
                  </Table>
                </div>

                {/* Comparación de scores */}
                <Card shadow="sm" padding="md" withBorder>
                  <Title order={4} mb="md">
                    <IconChartBar size={20} style={{ marginRight: 8 }} />
                    Mejora en Sostenibilidad
                  </Title>
                  <Group grow>
                    <Stack gap="xs">
                      <Text size="sm" c="dimmed">
                        Score Promedio Original
                      </Text>
                      <Text size="xl" fw={700}>
                        {(optimizedResult.average_score_original || 0).toFixed(1)}
                      </Text>
                    </Stack>
                    <Stack gap="xs">
                      <Text size="sm" c="dimmed">
                        Score Promedio Optimizado
                      </Text>
                      <Text size="xl" fw={700} c="green">
                        {(optimizedResult.average_score_optimized || 0).toFixed(1)}
                      </Text>
                    </Stack>
                  </Group>
                </Card>

                {(optimizedResult.items_removed || 0) > 0 && (
                  <Alert color="yellow" icon={<IconAlertCircle size={16} />}>
                    Se removieron {optimizedResult.items_removed} producto(s) para
                    ajustarse al presupuesto. Se mantuvieron los productos con mejor
                    relación valor/sostenibilidad.
                  </Alert>
                )}
              </>
            )}
          </Stack>
        </Card>
      )}
    </Stack>
  );
}

export default OptimizeList;