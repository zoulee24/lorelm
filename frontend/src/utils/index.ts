import request from './request'

function objectToFormData(obj: Record<string, any>, excludes?: string[]): FormData {
  const formData = new FormData();

  for (const key in obj) {
    if (!obj.hasOwnProperty(key)) continue;
    else if (excludes && excludes.includes(key)) continue
    // 判断是不是list
    _process(formData, key, obj[key])
  }
  return formData;
}

const _process = (form: FormData, key: string, value: any) => {
  if (Array.isArray(value)) {
    value.forEach((item, _) => {
      _process(form, key, item);
    });
  } else if (value instanceof File) {
    form.append(key, value, value.name);
  } else if (value !== undefined) {
    form.append(key, value);
  }
}

const showAvatar = (avatar?: string) =>
  (avatar ? '/file' + avatar : '/file/lorelm/resource/default_avatar.webp')

export { request, objectToFormData, showAvatar }