// ===============================
// FILE: src/fetchers/index.ts
// ===============================
// Interfaces y stubs de ingesta. Cablea tus fetchers reales aquí.

import type { LotteryId } from '../lotteries.spec';

export type QuinielaResultado = { 
  sorteo: 'DIA'|'NOCHE'; 
  fechaET: string; // ISO ET 
  premios: [number, number, number]; // 00–99 
  fuente: string; // dominio 
  urlFuente: string; 
};

export type PBResultado = { 
  fechaET: string; 
  blancos: [number,number,number,number,number]; 
  powerball: number; 
  powerPlay?: number; // 2,3,4,5,10 
  doublePlay?: boolean; 
  fuente: string; 
  urlFuente: string; 
};

export type MMResultado = { 
  fechaET: string; 
  blancos: [number,number,number,number,number]; 
  megaBall: number; 
  megaplier?: number; 
  fuente: string; 
  urlFuente: string; 
};

export type JC5Resultado = { 
  fechaET: string; 
  numeros: [number,number,number,number,number]; 
  xtra?: number;      // multiplicador aplicado 
  bullseye?: number;  // número Bullseye del sorteo 
  jackpotUSD?: number; 
  fuente: string; 
  urlFuente: string; 
};

export type AnyResultado = QuinielaResultado|PBResultado|MMResultado|JC5Resultado;

// Importar fetchers específicos
import { QuinielaFloridaFetcher } from './quiniela-florida';
import { PowerballFetcher } from './powerball';
import { MegaMillionsFetcher } from './mega-millions';
import { JerseyCash5Fetcher } from './jersey-cash5';

export async function fetchLatest(id: LotteryId): Promise<AnyResultado> { 
  switch (id) { 
    case 'quiniela_fl': 
      const qfFetcher = new QuinielaFloridaFetcher();
      return await qfFetcher.fetchResultado('DIA') || await qfFetcher.fetchSimulated('DIA');
    case 'powerball': 
      const pbFetcher = new PowerballFetcher();
      return await pbFetcher.fetchLatest() || await pbFetcher.fetchSimulated();
    case 'megamillions': 
      const mmFetcher = new MegaMillionsFetcher();
      return await mmFetcher.fetchLatest() || await mmFetcher.fetchSimulated();
    case 'jersey_cash_5': 
      const jc5Fetcher = new JerseyCash5Fetcher();
      return await jc5Fetcher.fetchLatest() || await jc5Fetcher.fetchSimulated();
  } 
}
