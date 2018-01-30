#!/bin/bash
export CLASSPATH=".:/usr/local/lib/antlr-4.7.1-complete.jar:$CLASSPATH"
alias antlr4='java -jar /usr/local/lib/antlr-4.7.1-complete.jar'       
antlr4 PS.g4 -o latex2sympy/gen                                    
