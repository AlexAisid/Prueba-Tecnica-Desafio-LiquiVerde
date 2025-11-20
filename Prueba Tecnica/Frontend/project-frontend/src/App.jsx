import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppShell, Container, Title, Group, Button } from '@mantine/core';
import { IconLeaf, IconHome, IconShoppingCart, IconChartBar, IconSearch } from '@tabler/icons-react';
import { Link } from 'react-router-dom';

// Pages
import Home from './pages/Home';
import SearchProducts from './pages/SearchProducts';
import ProductDetail from './pages/ProductDetail';
import OptimizeList from './pages/OptimizeList';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <AppShell
        header={{ height: 70 }}
        padding="md"
        styles={{
          main: {
            background: '#f5f5f5',
          },
        }}
      >
        <AppShell.Header>
          <Container size="xl" h="100%">
            <Group h="100%" justify="space-between">
              <Group>
                <IconLeaf size={32} color="#4caf50" />
                <Title order={2} c="green">
                  LiquiVerde
                </Title>
              </Group>

              <Group>
                <Button
                  component={Link}
                  to="/"
                  variant="subtle"
                  leftSection={<IconHome size={18} />}
                >
                  Inicio
                </Button>
                <Button
                  component={Link}
                  to="/search"
                  variant="subtle"
                  leftSection={<IconSearch size={18} />}
                >
                  Buscar
                </Button>
                <Button
                  component={Link}
                  to="/optimize"
                  variant="subtle"
                  leftSection={<IconShoppingCart size={18} />}
                >
                  Optimizar Lista
                </Button>
                <Button
                  component={Link}
                  to="/dashboard"
                  variant="subtle"
                  leftSection={<IconChartBar size={18} />}
                >
                  Estadísticas
                </Button>
              </Group>
            </Group>
          </Container>
        </AppShell.Header>

        <AppShell.Main>
          <Container size="xl">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<SearchProducts />} />
              <Route path="/product/:id" element={<ProductDetail />} />
              <Route path="/optimize" element={<OptimizeList />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </Container>
        </AppShell.Main>
      </AppShell>
    </Router>
  );
}

export default App;