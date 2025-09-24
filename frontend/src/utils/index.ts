import request from './request'

function objectToFormData(obj: Record<string, any>): FormData {
  const formData = new FormData();
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      formData.append(key, obj[key]);
    }
  }
  
  return formData;
}

export { request, objectToFormData }