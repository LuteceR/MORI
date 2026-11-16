import { mount } from '@vue/test-utils'
import { h } from 'vue'
import { describe, expect, test } from 'vitest'
import { componentStubs } from './component-stubs'
import AnnotatedToken from '../../app/components/AnnotatedToken.vue'
import DatasetEditorToolbar from '../../app/components/DatasetEditorToolbar.vue'
import MetricErrorLine from '../../app/components/MetricErrorLine.vue'
import MetricRunCard from '../../app/components/MetricRunCard.vue'
import PasswordField from '../../app/components/PasswordField.vue'
import ProjectCard from '../../app/components/ProjectCard.vue'
import ProjectCreateModal from '../../app/components/ProjectCreateModal.vue'
import ProjectDeleteModal from '../../app/components/ProjectDeleteModal.vue'
import RunModelDialog from '../../app/components/RunModelDialog.vue'

const global = { stubs: componentStubs }

describe('DatasetEditorToolbar', () => {
  test('Проверка компонента боковой панели датасетов на наличие основных кнопок', async () => {
    const wrapper = mount(DatasetEditorToolbar, {
      global,
      props: { 
        datasetPath: 'owner/dataset',
        showLabelControls: true
      }
    })

    expect(wrapper.text()).toContain('owner/dataset')
    const buttons = wrapper.findAll('button')
    await buttons[0]!.trigger('click')
    await buttons[1]!.trigger('click')
    await buttons[2]!.trigger('click')

    expect(wrapper.emitted('toggleFiles')).toHaveLength(1)
    expect(wrapper.emitted('toggleLabels')).toHaveLength(1)
    expect(wrapper.emitted('save')).toHaveLength(1)
  })

  test('Проверка компонента боковая панели на появление кнопки отображения существующих тегов при условии', () => {
    const wrapper = mount(DatasetEditorToolbar, {
      global,
      props: { 
        datasetPath: 'owner/dataset',
        showLabelControls: false
      }
    })

    expect(wrapper.findAll('button')).toHaveLength(2)
  })
})

describe('AnnotatedToken', () => {
  test('Проверка контекстного меню с считанным тэгами для токена датасета', async () => {
    const wrapper = mount(AnnotatedToken, {
      props: {
        word: 'Paris',
        rowIndex: 3,
        wordIndex: 2,
        colorClass: 'bg-sky-500'
      }
    })

    expect(wrapper.text()).toBe('Paris')
    expect(wrapper.get('span').classes()).toContain('bg-sky-500')
    await wrapper.get('span').trigger('contextmenu')
    expect(wrapper.emitted('contextmenu')?.[0]?.slice(1)).toEqual([3, 2])
  })
})

describe('PasswordField', () => {
  test('Проверка скрытия содержимого поля “Пароль” после нажатия на кнопку', async () => {
    const wrapper = mount(PasswordField, {
      global,
      slots: {
        default: ({ type, placeholder }: { type: string, placeholder: string }) =>
          h('input', { 'data-testid': 'password', type, placeholder })
      }
    })

    expect(wrapper.get('[data-testid="password"]').attributes('type')).toBe('password')
    await wrapper.get('button').trigger('click')
    expect(wrapper.get('[data-testid="password"]').attributes('type')).toBe('text')
    await wrapper.get('button').trigger('click')
    expect(wrapper.get('[data-testid="password"]').attributes('type')).toBe('password')
  })
})

// describe('ProjectCard', () => {
//   test('Проверка компонента модуля создания проекта', async () => {
//     const wrapper = mount(ProjectCard, {
//       global,
//       props: {
//         project: { 
//           id_projects: 23,
//           name: 'Research',
//           description: 'Project details'
//         }
//       }
//     })

//     expect(wrapper.text()).toContain('Research')
//     expect(wrapper.get('a').attributes('href')).toBe('/project/project/23')
//     await wrapper.get('button').trigger('click')
//     expect(wrapper.emitted('delete')).toEqual([['Research']])
//   })
// })

describe('ProjectCreateModal', () => {
  test('Проверка компонента модального окна создания проекта', async () => {
    const wrapper = mount(ProjectCreateModal, { global })
    const form = wrapper.get('form')
    const inputs = wrapper.findAll('input')

    await inputs[0]!.setValue('abc')
    await inputs[1]!.setValue('Description')
    await form.trigger('submit')
    expect(wrapper.emitted('submit')).toBeUndefined()

    await inputs[0]!.setValue('Project123')
    await form.trigger('submit')
    expect(wrapper.emitted('submit')).toEqual([[
      { projectName: 'Project123', projectDescription: 'Description' }
    ]])
  })
})

describe('ProjectDeleteModal', () => {
  test('Проверка компонента модального окна создания проекта на переадресацию на страницу редактирования проекта и срабатывания кнопки удаления', async () => {
    const wrapper = mount(ProjectDeleteModal, {
      global,
      props: {
        open: true,
        projectName: 'Research'
      }
    })

    expect(wrapper.text()).toContain('Удалить проект Research')
    await wrapper.get('button').trigger('click')

    expect(wrapper.emitted('confirm')).toHaveLength(1)
    expect(wrapper.emitted('update:open')).toEqual([[false]])
  })
})

// describe('RunModelDialog', () => {
//   test('Проверка компонента с содержанием метрик модели после запуска на определенном датасете', async () => {
//     const wrapper = mount(RunModelDialog, {
//       global,
//       props: {
//         models: ['model-a'],
//         datasets: ['dataset-a'],
//         modelName: '',
//         datasetName: '',
//         filePath: 'test.jsonl',
//         wordsKey: 'words',
//         nerKey: 'ner',
//         showThreshold: false,
//         thresholdValue: 0.5
//       }
//     })

//     const selects = wrapper.findAll('select')
//     await selects[0]!.setValue('model-a')
//     await selects[1]!.setValue('dataset-a')
//     const inputs = wrapper.findAll('input')
//     await inputs[0]!.setValue('input.jsonl')
//     await inputs[1]!.setValue('text')
//     await inputs[2]!.setValue('labels')
//     await inputs[3]!.setValue(true)
//     expect(wrapper.find('input[type="number"]').exists()).toBe(true)
//     await wrapper.find('input[type="number"]').setValue('0.75')

//     await wrapper.findAll('button').at(-1)!.trigger('click')
//     expect(wrapper.emitted('run')).toHaveLength(1)
//     expect(wrapper.emitted('update:modelName')?.at(-1)).toEqual(['model-a'])
//     expect(wrapper.emitted('update:datasetName')?.at(-1)).toEqual(['dataset-a'])
//     expect(wrapper.emitted('update:filePath')?.at(-1)).toEqual(['input.jsonl'])
//     expect(wrapper.emitted('update:wordsKey')?.at(-1)).toEqual(['text'])
//     expect(wrapper.emitted('update:nerKey')?.at(-1)).toEqual(['labels'])
//     expect(wrapper.emitted('update:showThreshold')?.at(-1)).toEqual([true])
//     expect(wrapper.emitted('update:thresholdValue')?.at(-1)).toEqual(['0.75'])
//   })
// })

// describe('MetricRunCard', () => {
//   const metric = {
//     id_metrics: 8,
//     name: 'model-a',
//     name_1: 'dataset-a',
//     date: '2026-10-26',
//     metrics_data: [{ name: 'F1', value: 0.91234 }]
//   }

//   test('отображение деталей запуска, округлённых результатов до 4 знаков после запятой, наличие ссылки на результат и проверка кнопки удаления результатов запуска', async () => {
//     const wrapper = mount(MetricRunCard, {
//       global,
//       props: { metric, index: 1, editMode: false }
//     })

//     expect(wrapper.text()).toContain('Запуск #2')
//     expect(wrapper.text()).toContain('Модель model-a')
//     expect(wrapper.text()).toContain('Датасет dataset-a')
//     expect(wrapper.text()).toContain('F1: 0.9123')
//     expect(wrapper.get('a').attributes('href')).toBe('/metrics/8')
//     expect(wrapper.findAll('button')).toHaveLength(0)

//     await wrapper.setProps({ editMode: true })
//     await wrapper.find('button').trigger('click')
//     expect(wrapper.emitted('remove')).toHaveLength(1)
//   })
// })

// describe('MetricErrorLine', () => {
//   test('highlights the error token and associates predicted and true labels correctly', () => {
//     const wrapper = mount(MetricErrorLine, {
//       global,
//       props: {
//         errorLine: {
//           word_id: 1,
//           words: ['A', 'very-long-word'],
//           true_labels: ['O', 'B-PER'],
//           pred_labels: ['O', 'B-ORG']
//         }
//       }
//     })

//     expect(wrapper.text()).toContain('very-long-word')
//     expect(wrapper.text()).toContain('pred: B-ORG')
//     expect(wrapper.text()).toContain('true: B-PER')
//     expect(wrapper.findAll('.border-2.border-red-500')).toHaveLength(1)
//   })

//   test('truncates long tokens in the rendered word', () => {
//     const longWord = 'x'.repeat(60)
//     const wrapper = mount(MetricErrorLine, {
//       global,
//       props: {
//         errorLine: {
//           word_id: 0,
//           words: [longWord],
//           true_labels: ['O'],
//           pred_labels: ['O']
//         }
//       }
//     })

//     expect(wrapper.text()).toContain(`${'x'.repeat(50)}...`)
//     expect(wrapper.text()).not.toContain(longWord)
//   })
// })