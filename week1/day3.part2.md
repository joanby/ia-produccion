# Día 3 Parte 2: Añadir suscripciones con Clerk Billing

## Transforma tu SaaS con gestión de suscripciones

Ahora añadiremos niveles de suscripción a tu Generador de Ideas de Negocio, convirtiéndolo en un SaaS completo con procesamiento de pagos y gestión de suscripciones integrada.

## Lo que construirás

Una versión mejorada de tu app que:
- Exige una suscripción de pago para acceder al generador de ideas
- Muestra una tabla de precios atractiva a quienes no están suscritos
- Gestiona el procesamiento de pagos mediante Clerk Billing
- Administra el estado de suscripción automáticamente
- Ofrece un menú de usuario con opciones de facturación

## Requisitos previos

- Haber completado el Día 3 Parte 1 (autenticación funcionando)
- Tu app desplegada en Vercel

## Paso 1: Habilita Clerk Billing

### Navega al panel de Clerk

1. Ve a tu [Clerk Dashboard](https://dashboard.clerk.com)
2. Selecciona tu aplicación **SaaS**
3. Haz clic en **Configure** en la navegación superior
4. Haz clic en **Subscription Plans** en la barra lateral izquierda
5. Pulsa **Get Started** si es la primera vez

### Activa la facturación

1. Pulsa **Enable Billing** si se te solicita
2. Acepta los términos si aparece el aviso
3. Verás la página de Subscription Plans

## Paso 2: Crea tu plan de suscripción

### Configura el plan

1. Haz clic en **Create Plan**
2. Completa los detalles:
   - **Name:** Premium Subscription
   - **Key:** `premium_subscription` (es importante; cópialo exactamente)
   - **Price:** $10.00 mensual (o el precio que prefieras)
   - **Description:** Unlimited AI-powered business ideas
3. Opcional: añade un descuento anual
   - Activa **Annual billing**
   - Establece el precio anual (ej., $100/año como descuento)
4. Haz clic en **Save**

### Copia el ID del plan

Después de crear el plan verás un **Plan ID** en la esquina superior derecha de la tarjeta (algo como `plan_...`). Lo necesitas para pruebas, aunque Clerk lo maneja automáticamente en producción.

## Paso 3: Actualiza tu página de producto

Como usamos Pages Router con componentes del lado del cliente, necesitamos proteger la ruta del producto con una verificación de suscripción.

Actualiza `pages/product.tsx`:

```typescript
"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useAuth } from '@clerk/nextjs';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { Protect, PricingTable, UserButton } from '@clerk/nextjs';

function IdeaGenerator() {
    const { getToken } = useAuth();
    const [idea, setIdea] = useState<string>('…loading');

    useEffect(() => {
        let buffer = '';
        (async () => {
            const jwt = await getToken();
            if (!jwt) {
                setIdea('Authentication required');
                return;
            }
            
            await fetchEventSource('/api', {
                headers: { Authorization: `Bearer ${jwt}` },
                onmessage(ev) {
                    buffer += ev.data;
                    setIdea(buffer);
                },
                onerror(err) {
                    console.error('SSE error:', err);
                    // Don't throw - let it retry
                }
            });
        })();
    }, []); // Empty dependency array - run once on mount

    return (
        <div className="container mx-auto px-4 py-12">
            {/* Header */}
            <header className="text-center mb-12">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                    Business Idea Generator
                </h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    AI-powered innovation at your fingertips
                </p>
            </header>

            {/* Content Card */}
            <div className="max-w-3xl mx-auto">
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
                    {idea === '…loading' ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-pulse text-gray-400">
                                Generating your business idea...
                            </div>
                        </div>
                    ) : (
                        <div className="markdown-content text-gray-700 dark:text-gray-300">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkBreaks]}
                            >
                                {idea}
                            </ReactMarkdown>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function Product() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {/* User Menu in Top Right */}
            <div className="absolute top-4 right-4">
                <UserButton showName={true} />
            </div>

            {/* Subscription Protection */}
            <Protect
                plan="premium_subscription"
                fallback={
                    <div className="container mx-auto px-4 py-12">
                        <header className="text-center mb-12">
                            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                                Choose Your Plan
                            </h1>
                            <p className="text-gray-600 dark:text-gray-400 text-lg mb-8">
                                Unlock unlimited AI-powered business ideas
                            </p>
                        </header>
                        <div className="max-w-4xl mx-auto">
                            <PricingTable />
                        </div>
                    </div>
                }
            >
                <IdeaGenerator />
            </Protect>
        </main>
    );
}
```

## Paso 4: Actualiza tu landing page

Actualicemos la landing para que refleje mejor el modelo de suscripción.

Actualiza `pages/index.tsx`:

```typescript
"use client"

import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            IdeaGen Pro
          </h1>
          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-4">
                <Link 
                  href="/product" 
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>
                <UserButton showName={true} />
              </div>
            </SignedIn>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-24">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Generate Your Next
            <br />
            Big Business Idea
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
            Harness the power of AI to discover innovative business opportunities tailored for the AI agent economy
          </p>
          
          {/* Pricing Preview */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 max-w-sm mx-auto mb-8">
            <h3 className="text-2xl font-bold mb-2">Premium Subscription</h3>
            <p className="text-4xl font-bold text-blue-600 mb-2">$10<span className="text-lg text-gray-600">/month</span></p>
            <ul className="text-left text-gray-600 dark:text-gray-400 mb-6">
              <li className="mb-2">✓ Unlimited idea generation</li>
              <li className="mb-2">✓ Advanced AI models</li>
              <li className="mb-2">✓ Priority support</li>
            </ul>
          </div>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Start Your Free Trial
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Access Premium Features
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </main>
  );
}
```

## Paso 5: Configura el proveedor de pagos (opcional)

Clerk incluye un gateway de pagos listo para usarse de inmediato:

1. En el panel de Clerk → **Configure** → **Billing** → **Settings** (barra lateral izquierda)
2. De forma predeterminada está seleccionado **Clerk payment gateway**:
   - "Nuestro gateway de cero configuración. Listo para procesar pagos de prueba inmediatamente."
   - Perfecto para pruebas y desarrollo
3. **Opcional:** puedes cambiar a Stripe si lo prefieres:
   - Selecciona **Stripe**
   - Sigue el asistente de Clerk para conectar tu cuenta de Stripe

**Nota:** el gateway de Clerk es ideal para comenzar: procesa pagos de prueba al instante sin configuración adicional.

## Paso 6: Prueba el flujo de suscripción

Despliega tu aplicación actualizada:

```bash
vercel --prod
```

### Probando el flujo

1. Visita tu URL de producción
2. Inicia sesión (o crea una cuenta nueva)
3. Haz clic en "Go to App" o "Access Premium Features"
4. Verás la tabla de precios porque aún no tienes suscripción
5. Haz clic en **Subscribe** en el plan Premium
6. Si no conectaste un proveedor de pagos, Clerk simulará la suscripción
7. Después de suscribirte tendrás acceso al generador de ideas

### Gestión de suscripciones

Las personas pueden administrar su suscripción desde el menú del UserButton:
1. Haz clic en su foto de perfil (UserButton)
2. Selecciona **Manage account**
3. Ve a **Subscriptions**
4. Consulta o cancela la suscripción

## ¿Qué está pasando?

Tu app ahora cuenta con:
- **Filtro por suscripción**: hace falta una suscripción activa para usar el producto
- **Tabla de precios**: diseño atractivo gestionado por Clerk
- **Procesamiento de pagos**: manejado completamente por Clerk (o Stripe si lo conectas)
- **Gestión de usuarios**: estado de suscripción visible en el UserButton
- **Aplicación automática**: Clerk verifica el estado de suscripción de forma transparente

## Resumen de la arquitectura

1. **La persona visita `/product`** → Clerk revisa su suscripción
2. **Sin suscripción** → se muestra el componente PricingTable
3. **Con suscripción** → se muestra el componente IdeaGenerator
4. **Pago** → lo gestiona Clerk Billing (o Stripe)
5. **Gestión** → las personas administran su suscripción desde la interfaz de Clerk

## Resolución de problemas

### Error "Plan not found"
- Asegúrate de que la clave del plan sea exactamente `premium_subscription`
- Revisa que la facturación esté habilitada en el panel de Clerk
- Verifica que el plan esté activo (no archivado)

### La tabla de precios no aparece
- Borra caché y cookies del navegador
- Comprueba que `@clerk/nextjs` esté actualizado
- Asegura que la facturación esté habilitada en tu aplicación de Clerk

### Siempre ves la tabla de precios (incluso tras suscribirte)
- Revisa el estado de la suscripción de ese usuario en el panel de Clerk
- Verifica que la clave del plan coincida exactamente
- Intenta cerrar sesión y volver a entrar

### El pago no funciona
- Es normal si no conectaste un proveedor de pagos
- Clerk simulará las suscripciones en modo de prueba
- Para pagos reales, conecta Stripe en Billing Settings

## Opciones de personalización

### Distintos niveles de plan

Puedes crear varios planes en el panel de Clerk:
```typescript
<Protect
    plan={["basic_plan", "premium_plan", "enterprise_plan"]}
    fallback={<PricingTable />}
>
    <IdeaGenerator />
</Protect>
```

### Tabla de precios personalizada

En lugar de la PricingTable de Clerk, puedes construir la tuya:
```typescript
<Protect
    plan="premium_subscription"
    fallback={<CustomPricingPage />}
>
    <IdeaGenerator />
</Protect>
```

### Límites de uso

Controla el uso de la API por persona en tu backend:
```python
@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("subscription", "free")
    
    # Apply different limits based on plan
    if subscription_plan == "premium_subscription":
        # Unlimited or high limit
        pass
    else:
        # Limited access
        pass
```

## Próximos pasos

¡Felicidades! Construiste un SaaS completo con:
- ✅ Autenticación de usuarios
- ✅ Gestión de suscripciones
- ✅ Procesamiento de pagos
- ✅ Funcionalidades impulsadas por IA
- ✅ UI/UX profesional

### Ideas para mejorar

1. **Múltiples niveles de suscripción** (Basic, Pro, Enterprise)
2. **Seguimiento de uso** y límites por nivel
3. **Integración de webhooks** para eventos de suscripción
4. **Notificaciones por email** ante cambios de suscripción
5. **Panel de administración** para gestionar usuarios y suscripciones
6. **Descuentos por facturación anual**
7. **Periodos de prueba gratis**

¡Tu Generador de Ideas de Negocio ahora es un producto SaaS completo listo para clientes reales!
