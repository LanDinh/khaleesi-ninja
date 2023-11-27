export type DataMapper<Data> = (data: Data) => string

export type TableColumn<Data> = {
  label: string,
  value : DataMapper<Data>,
}
