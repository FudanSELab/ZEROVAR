当前测试主要问题：
> 1. 第一步生成的注释有时为空，例如CODE2。
> 2. 生成拓展词的时候，有时会出现补 @param / @throw / @return 等情况。
> 3. 预测的结果里，有时会引入新的掩码，例如 CODE2-3 attrURI。
> 4. 一些不常见的缩写，即使是代码里有对应的全称，也预测不出来。例如 CODE2-2 nsme。  

<br>

下文格式说明：
> - 测试代码编号
> - 测试代码本体
> - 缩写词测试结果
>   - 缩写词=>全称
>   - 模型给出的结果
>   - 发现的一些额外问题或补测结果

<br>

---

<br>

#### CODE 1

```java
public static String getterName(Class<?> componentClass) {
	if (componentClass == null) return null;
	StringBuilder sb = new StringBuilder("get");
    sb.append(componentClass.getSimpleName()); 
	return sb.toString();
}
```
1. **sb** => StringBuilder

```shell
['the builder', 'the string builder', 'the buffer', 'the builder to append to', 'the sb', 'the builder to use', 'the StringBuilder', 'the source code builder', 'the source code buffer', 'the builder to add to']
```

> *如果代码里是StringBuffer呢？*
> 
> ```shell
> ['the builder', 'the buffer', 'the string builder', 'the sb', 'the StringBuffer', 'the builder to append to', 'the builder to use', 'the source code buffer', 'the source code builder', 'the builder to add to']
> ```

<br>

#### CODE 2
```java
boolean setAttrValue(
          StylesheetHandler handler, String attrUri, String attrLocalName, 
          String attrRawName, String attrValue, ElemTemplateElement elem)
            throws org.xml.sax.SAXException
  {
    if(attrRawName.equals("xmlns") || attrRawName.startsWith("xmlns:"))
      return true;
      
    String setterString = getSetterMethodName();

    // If this is null, then it is a foreign namespace and we 
    // do not process it.
    if (null != setterString)
    {
      try
      {
        Method meth;
        Object[] args;

        if(setterString.equals(S_FOREIGNATTR_SETTER))
        {
          // workaround for possible crimson bug
          if( attrUri==null) attrUri="";
          // First try to match with the primative value.
          Class sclass = attrUri.getClass();
          Class[] argTypes = new Class[]{ sclass, sclass,
                                      sclass, sclass };
  
          meth = elem.getClass().getMethod(setterString, argTypes);
  
          args = new Object[]{ attrUri, attrLocalName,
                                      attrRawName, attrValue };
        }
        else
        {
          Object value = processValue(handler, attrUri, attrLocalName,
                                      attrRawName, attrValue, elem);
          // If a warning was issued because the value for this attribute was
          // invalid, then the value will be null.  Just return
          if (null == value) return false;
                                      
          // First try to match with the primative value.
          Class[] argTypes = new Class[]{ getPrimativeClass(value) };
  
          try
          {
            meth = elem.getClass().getMethod(setterString, argTypes);
          }
          catch (NoSuchMethodException nsme)
          {
            Class cl = ((Object) value).getClass();
  
            // If this doesn't work, try it with the non-primative value;
            argTypes[0] = cl;
            meth = elem.getClass().getMethod(setterString, argTypes);
          }
  
          args = new Object[]{ value };
        }

        meth.invoke(elem, args);
      }
      catch (NoSuchMethodException nsme)
      {
        if (!setterString.equals(S_FOREIGNATTR_SETTER)) 
        {
          handler.error(XSLTErrorResources.ER_FAILED_CALLING_METHOD, new Object[]{setterString}, nsme);//"Failed calling " + setterString + " method!", nsme);
          return false;
        }
      }
      catch (IllegalAccessException iae)
      {
        handler.error(XSLTErrorResources.ER_FAILED_CALLING_METHOD, new Object[]{setterString}, iae);//"Failed calling " + setterString + " method!", iae);
        return false;
      }
      catch (InvocationTargetException nsme)
      {
        handleError(handler, XSLTErrorResources.WG_ILLEGAL_ATTRIBUTE_VALUE,
            new Object[]{ Constants.ATTRNAME_NAME, getName()}, nsme);
        return false;
      }
    }
    
    return true;
}
```

**模型第一步没能生成出注释。**

1. **meth** => method :white_check_mark:

```shell
['Method to call', 'Method name', 'Method called', 'The method', 'Method', 'Method to invoke', 'Method to execute', 'Method invoked', 'Method object', '']
```


2. **nsme** => NoSuchMethodException :negative_squared_cross_mark:

```shell
['TODO', 'The namespace', 'The attribute name', 'the namespace', 'The namespace name', 'The element', 'The element name', 'The name of the namespace', 'The namespace<mask1>', 'The name of the element']
```

> 不常见的缩写，会被匹配成更常见的全称，如这里的namespace，但是对应缩写应该是nmse才对。

3. **attrUri** => The Namespace URI of the attribute :white_check_mark:

```shell
['attribute URI', 'attribute uri', 'The namespace URI', '@return true if successful', '@param attrLocalName\n@param attrValue\n@param elem', 'The URI of the attribute<mask1>Handler', '@param attrLocalName\n@param attrRawName', '@param attrLocalName\n@param attrRawName\n@param attrValue\n@param elem', 'The URI of the attribute<mask1>String', '@param attrLocalName\n@param attrValue']
```

> 因为没能生成注释，所以补充时把attrUri后面的参数注释补上了 => 第一步的注释生成效果不佳会导致第二步的补齐出现问题。
>
> 为什么生成结果里也带掩码，\<mask1>？

4. **iae** =>  IllegalAccessException :negative_squared_cross_mark:

```shell
['h', 'The attribute value', 'attribute value', 'The attribute name', 'the attribute name', 'the attribute value', 'The element', 'The value to set', '@return boolean', '@param elem']
```
<br>

#### CODE 3

```Java
public static boolean intersects(SpatialComparable box1, SpatialComparable box2) {
    final int dim = assertSameDimensionality(box1, box2);
    for(int i = 0; i < dim; i++) {
      if(box2.getMax(i) < box1.getMin(i) || box1.getMax(i) < box2.getMin(i)) {
        return false;
      }
    }
    return true;
  }
```
1. **dim**=>dimension
```shell
['Dimension', 'The dimension', 'Dimensionality', 'the dimension', 'Number of dimensions', 'The dimensionality', 'the dimensionality', 'dimension', 'The dim', 'The dimensions']
```
> dim到dimension和dimensionality，有两种相似词的结果。

<br>

#### CODE 4

```Java
    public void setSessionTimeout(Long timeout, TimeUnit unit) {
        long t = unit.toMillis(timeout);
        properties.put("request.timeout.ms", String.valueOf(t + 60000));
        properties.put("session.timeout.ms", String.valueOf(t));
    }
```
1. **t** => timeout
```shell
['the timeout', 'the timeout', 'the timeout t', 'the timeout', 'the timeout t', 'the timeout', 'the t', 'the timeout value', 'the timeout', 'the timeout value']
```

<br>

#### CODE 5

```Java
private String resolveServiceEntry(String serviceType, String domain,
                        DirContext ctx) {
                String result = null;
                try {
                        String query = new StringBuilder("_").append(serviceType).append("._tcp.")
                                        .append(domain).toString();
                        Attribute dnsRecord = lookup(query, ctx, "SRV");
                        // There are maybe more records defined, we will return the one
                        // with the highest priority (lowest number) and the highest weight
                        // (highest number)
                        int highestPriority = -1;
                        int highestWeight = -1;

                        for (NamingEnumeration<?> recordEnum = dnsRecord.getAll(); recordEnum
                                        .hasMoreElements();) {
                                String[] record = recordEnum.next().toString().split(" ");
                                if (record.length != 4) {
                                        throw new DnsLookupException("Wrong service record for query " + query
                                                        + ": [" + Arrays.toString(record) + "]");
                                }
                                int priority = Integer.parseInt(record[0]);
                                int weight = Integer.parseInt(record[1]);
                                // we have a new highest Priority, so forget also the highest weight
                                if (priority < highestPriority || highestPriority == -1) {
                                        highestPriority = priority;
                                        highestWeight = weight;
                                        result = record[3].trim();
                                }
                                // same priority, but higher weight
                                if (priority == highestPriority && weight > highestWeight) {
                                        highestWeight = weight;
                                        result = record[3].trim();
                                }
                        }
                }
                catch (NamingException e) {
                        throw new DnsLookupException(
                                        "DNS lookup failed for service " + serviceType + " at " + domain, e);
                }

                // remove the "." at the end
                if (result.endsWith(".")) {
                        result = result.substring(0, result.length() - 1);
                }
                return result;
        }
```

1. **ctx** => context
```shell
['context', '', 'directory context', 'Context', 'DirContext', 'the context', 'The DirContext', 'The context', 'the DirContext', 'DirectoryContext']
```
> 代码中为`DirContext ctx`，那么`ctx`是拓展到`context`就可以，还是要拓展到`DirContext`呢？

<br>

#### CODE 6

```Java
private List<InMemoryMappingFile> copyInMemoryMappingFiles(List<InMemoryMappingFile> copyIMMF) {
        List<InMemoryMappingFile> immf = new ArrayList<InMemoryMappingFile>();
        for (InMemoryMappingFile file : copyIMMF) {
            immf.add(new InMemoryMappingFile(file.getMappingFile()));
        }
        return immf;
    }
```
1. **immf** =》 InMemoryMappingFile
```shell
['', '@throws IOException', 'List', 'list', 'List', '@return', 'The list', '@throws Exception', '@deprecated', '']
```
> 即使是代码中提到了 `InMemoryMappingFile` ,依然预测失败了，更倾向于预测称代码的类型。

<br>

#### CODE 7
```Java
public WebReply performInitialChecks(WebRequest webRequest, String uriName) {
        WebReply webReply = null;
        HttpServletRequest req = webRequest.getHttpServletRequest();
        String methodName = req.getMethod();

        if (uriName == null || uriName.length() == 0) {
            return new DenyReply("Invalid URI passed to Security Collaborator.");
        }

        if (unsupportedAuthMech() == true) {
            return new DenyReply("Authentication Failed : DIGEST not supported");
        }

        if (wasch.isSSLRequired(webRequest, uriName)) {
            return httpsRedirectHandler.getHTTPSRedirectWebReply(req);
        }

        webReply = unprotectedSpecialURI(webRequest, uriName, methodName);
        if (webReply != null) {
            return webReply;
        }

        webReply = unprotectedResource(webRequest);
        if (webReply == PERMIT_REPLY) {
            if (shouldWePerformTAIForUnProtectedURI(webRequest))
                return null;
            else
                return webReply;
        }

        return null;
    }
```
1. **req** => request
```shell
['the request', 'The request', '', 'Request', '@return', 'request', 'The request object', 'Request object', 'The servlet request', 'the request']
```
<br>

#### CODE 8
```Java
protected synchronized void invoke()
   {
      if (TraceComponent.isAnyTracingEnabled() && tc.isEntryEnabled()) SibTr.entry(this, tc, "invoke");

      //Have a quick look at the conversation, if it is not closed invoke the receive listener.
      if(!conversation.isClosed())
      {
         try
         {
            ConversationReceiveListener newReceiveListener = null;
            
            do
            {
               // Remember details about the byte buffer we pass in, in case
               // it is changed.
               int position = data.position();
               int limit = data.limit();

               // Pass details to implementor's conversation receive listener.
               if (TraceComponent.isAnyTracingEnabled() && tc.isDebugEnabled()) JFapUtils.debugTraceWsByteBuffer(this, tc, data, 16, "data passed to dataReceived method");
               newReceiveListener =
                 listener.dataReceived(data,
                                        segmentType,
                                        requestNumber,
                                        priority,
                                        allocatedFromPool,
                                        partOfExchange,
                                        conversation);

               if (newReceiveListener != null)
               {
                  // If implementor supplies a different listener, make this
                  // take effect.
                  if (TraceComponent.isAnyTracingEnabled() && tc.isDebugEnabled()) SibTr.debug(this, tc, "new receive listener supplied: "+newReceiveListener);
                  ((ConversationImpl)conversation).setDefaultReceiveListener(newReceiveListener);
                  listener = newReceiveListener;
                  data.limit(limit);
                  data.position(position);
               }
            }
            while(newReceiveListener != null);
         }
         catch(Throwable t)
         {
            FFDCFilter.processException
               (t, "com.ibm.ws.sib.jfapchannel.impl.rldispatcher.ConversationReceiveListenerDataReceivedInvocation.invoke", JFapChannelConstants.CRLDATARECEIVEDINVOKE_INVOKE_01);
            if (TraceComponent.isAnyTracingEnabled() && tc.isDebugEnabled()) SibTr.debug(this, tc, "exception thrown by dataReceived");
            if (TraceComponent.isAnyTracingEnabled() && tc.isEventEnabled()) SibTr.exception(this, tc, t);

            // User has thrown an exception from data received method.  Probably
            // the best way to deal with this is to invalidate their connection.
            // That'll learn 'em.
            connection.invalidate(true, t, "execption thrown by dataReceived method - "+t.getMessage());    // D224570

         }
      }
      else
      {
         if(TraceComponent.isAnyTracingEnabled() && tc.isDebugEnabled()) SibTr.debug(this, tc, "Conversation was already closed bypassing invoke.");
      }

      if (TraceComponent.isAnyTracingEnabled() && tc.isEntryEnabled()) SibTr.exit(this, tc, "invoke");
   }
```
1. **tc** => TraceComponent
```shell
['The current trace context<mask1>', 'the current trace context<mask1>', 'the tc<mask1>', 'the current thread<mask1>', 'The current thread<mask1>', 'The current thread<mask1>Thread', 'The current tc<mask1>', 'The current trace<mask1>Thread', 'The current trace<mask1>er', 'the current thread<mask1>Thread']
```
2. **t** => Throwable
```shell
['The throwable<mask1>', 'the throwable<mask1>', 'The Throwable<mask1>', 'the Throwable<mask1>', 'The exception<mask1>', 'the exception<mask1>', 'The throwable<mask1>Exception', 'the throwable<mask1>Exception', '@throws Throwable Thrown<mask1>Exception', '']
```

#### CODE 9
```Java
public static String toJavaDatePattern(String format) {

        int          len = format.length();
        char         ch;
        StringBuffer sb        = new StringBuffer(len);
        Tokenizer    tokenizer = new Tokenizer();

        for (int i = 0; i <= len; i++) {
            ch = (i == len) ? e
                            : format.charAt(i);

            if (!tokenizer.next(ch, dateTokens)) {
                int index = tokenizer.getLastMatch();

                if (index >= 0) {
                    sb.setLength(sb.length() - tokenizer.length());
                    sb.append(javaDateTokens[index]);
                }

                tokenizer.reset();

                if (tokenizer.isConsumed()) {
                    continue;
                }
            }

            sb.append(ch);
        }

        sb.setLength(sb.length() - 1);

        String javaPattern = sb.toString();

        return javaPattern;
    }
```
1. **ch** => char
```shell
['the ch', 'the ch', 'the ch', 'the character', 'the character used', 'the character to use', 'the character used', 'the chord', 'the character to use', 'the character to match']
```
2. **sb** => StringBuffer
```shell
['the buffer', 'the string builder', 'the StringBuffer', 'the StringBuilder', 'the buffer to use', 'the string buffer', 'the buffer', 'the buffer', 'the StringBuffer to use', '']
```
> 代码变长了以后，预测结果里同时有StringBuffer和StringBuilder

<br>

#### CODE 10
```Java
public static String resolveLocaleCode(String lang, String country, String variant) {
	StringBuilder code = new StringBuilder(lang);
	if (!StringUtils.isEmpty(country)) {
		code.append('_').append(country);
		if (!StringUtils.isEmpty(variant)) {
			code.append('_').append(variant);
		}
	}
	return code.toString();
}
```
1. **lang** => language
```shell
['the language', 'the lang', 'the language code', 'the locale', 'a language', 'the language name', 'language', 'unknown', 'the language only', 'is the language']
```

