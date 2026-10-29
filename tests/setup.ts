import { h } from 'vue'
import { ref } from 'vue'
import { vi } from 'vitest'

vi.mock('@clerk/vue', () => ({
  Show: {
    props: ['when'],
    setup(props: { when: string }, context: { slots: { default?: () => unknown } }) {
      return () => (props.when === 'signed-out' ? h('div', context.slots.default?.() as any) : null)
    },
  },
  SignInButton: {
    setup(_: unknown, context: { slots: { default?: () => unknown } }) {
      return () => h('div', context.slots.default?.() as any)
    },
  },
  SignUpButton: {
    setup(_: unknown, context: { slots: { default?: () => unknown } }) {
      return () => h('div', context.slots.default?.() as any)
    },
  },
  UserButton: { template: '<button type="button">Usuario</button>' },
  useAuth: vi.fn(() => ({
    isLoaded: ref(true),
    isSignedIn: ref(true),
    getToken: ref(vi.fn().mockResolvedValue('token-de-prueba')),
  })),
}))
