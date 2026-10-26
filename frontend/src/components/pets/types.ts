export type SpeciesId = 'cat' | 'dog' | 'rabbit' | 'panda' | 'fox' | 'dragon'
export type PetLevel = 1 | 2 | 3 | 4 | 5
export type PetMood = 'happy' | 'neutral' | 'sad'
export type PetReactionType = 'cheer' | 'comfort' | 'evolve'

export interface PetReaction {
  type: PetReactionType
  nonce: number
}