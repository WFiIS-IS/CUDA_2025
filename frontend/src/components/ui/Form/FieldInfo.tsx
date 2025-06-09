import type { AnyFieldApi } from '@tanstack/react-form';

export type FieldInfoProps = {
  field: AnyFieldApi;
};

export function FieldInfo({ field }: FieldInfoProps) {
  return (
    <>
      {field.state.meta.isTouched && !field.state.meta.isValid ? (
        <p className="text-destructive text-sm">{field.state.meta.errors.map((error) => error.message).join(', ')}</p>
      ) : null}
    </>
  );
}
