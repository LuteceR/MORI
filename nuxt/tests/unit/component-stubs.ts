import { defineComponent, h } from 'vue'

export const componentStubs = {
  UButton: defineComponent({
    name: 'UButton',
    props: ['label', 'to', 'type'],
    emits: ['click'],
    setup(props, { emit, slots }) {
      return () => h(
        props.to ? 'a' : 'button',
        {
          href: props.to,
          type: props.type || 'button',
          onClick: (event: MouseEvent) => emit('click', event)
        },
        slots.default?.() ?? props.label
      )
    }
  }),
  UCard: defineComponent({
    name: 'UCard',
    props: ['title', 'description'],
    setup(props, { slots }) {
      return () => h('article', [
        h('h2', props.title),
        h('p', props.description),
        slots.header?.(),
        slots.default?.()
      ])
    }
  }),
  UFieldGroup: defineComponent({
    name: 'UFieldGroup',
    setup(_, { slots }) {
      return () => h('div', slots.default?.())
    }
  }),
  UContainer: defineComponent({
    name: 'UContainer',
    setup(_, { slots }) {
      return () => h('div', slots.default?.())
    }
  }),
  ULink: defineComponent({
    name: 'ULink',
    props: ['to'],
    setup(props, { slots }) {
      return () => h('a', { href: props.to }, slots.default?.())
    }
  }),
  UFormField: defineComponent({
    name: 'UFormField',
    props: ['label'],
    setup(props, { slots }) {
      return () => h('label', [props.label, slots.default?.()])
    }
  }),
  UForm: defineComponent({
    name: 'UForm',
    props: ['schema', 'state'],
    emits: ['submit'],
    setup(props, { emit, slots }) {
      return () => h('form', {
        onSubmit: (event: Event) => {
          event.preventDefault()
          const result = props.schema.safeParse(props.state)
          if (result.success) {
            emit('submit', { data: result.data })
          }
        }
      }, slots.default?.())
    }
  }),
  UInput: defineComponent({
    name: 'UInput',
    props: ['modelValue', 'type', 'placeholder'],
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      return () => h('input', {
        value: props.modelValue,
        type: props.type || 'text',
        placeholder: props.placeholder,
        onInput: (event: Event) => emit('update:modelValue', (event.target as HTMLInputElement).value)
      })
    }
  }),
  USelectMenu: defineComponent({
    name: 'USelectMenu',
    props: ['modelValue', 'items', 'placeholder'],
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      return () => h('select', {
        value: props.modelValue,
        onChange: (event: Event) => emit('update:modelValue', (event.target as HTMLSelectElement).value)
      }, [
        h('option', { value: '' }, props.placeholder),
        ...(props.items as string[]).map(item => h('option', { value: item }, item))
      ])
    }
  }),
  UCheckbox: defineComponent({
    name: 'UCheckbox',
    props: ['modelValue'],
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      return () => h('input', {
        type: 'checkbox',
        checked: props.modelValue,
        onChange: (event: Event) => emit('update:modelValue', (event.target as HTMLInputElement).checked)
      })
    }
  }),
  UModal: defineComponent({
    name: 'UModal',
    emits: ['update:open'],
    setup(_, { slots, emit }) {
      return () => h('section', [
        slots.default?.(),
        slots.body?.(),
        slots.footer?.({ close: () => emit('update:open', false) })
      ])
    }
  }),
  UPopover: defineComponent({
    name: 'UPopover',
    setup(_, { slots }) {
      return () => h('div', [slots.default?.(), slots.content?.()])
    }
  }),
  UTooltip: defineComponent({
    name: 'UTooltip',
    setup(_, { slots }) {
      return () => h('div', slots.default?.())
    }
  })
}
