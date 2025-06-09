import type { AnyFieldApi } from '@tanstack/react-form';

export type FieldInfoProps = {
  field: AnyFieldApi;
};

export function FieldInfo({ field }: FieldInfoProps) {
  return (
    <>
      {field.state.meta.isTouched && !field.state.meta.isValid ? <em>{field.state.meta.errors.join(', ')}</em> : null}
      {field.state.meta.isValidating ? 'Validating...' : null}
    </>
  );
}
